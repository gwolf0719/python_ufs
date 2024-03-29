#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime 
import time
import numpy as np
from pandas.core.frame import DataFrame

# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *
from data_model.tags import *


# line bot 相關元件
from linebot import LineBotApi
from linebot.models import *
from linebot.exceptions import LineBotApiError


class Tags:
    def __init__(self):
        # self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.client.admin.authenticate('james', 'wolf0719')
        self.col_tag_main = self.client.ufs.tag_main
        self.col_tag_log = self.client.ufs.tag_log
        self.col_user = self.client.ufs.users
        

    # 新增標籤主表資料
    # ===============================
  
    def set_tag_main(self,tag_data):
        self.col_tag_main.insert_one(tag_data)
        return True
    # 取得所有追縱標籤資料 used=None 表示不用篩選已經用過的
    def get_tag_list(self,channel_id,used=None):
        if used is None:
            # tag_list = self.col_tag_main.find({"channel_id":channel_id})
            tag_list = []
            for tag in self.col_tag_main.find({"channel_id":channel_id}):
                del(tag['_id'])
                tag_list.append(tag)
            
            return list(tag_list)
        else:
            # 2020-10-25 已經整併 all_tags_users
            return Tags().all_tags_users(channel_id)
    
   
    # 確認 tag 要被追縱處理
    def chk_once(self,channel_id,tag):
        find = {
            "channel_id":channel_id,
            "tag":tag
        }
        if(self.col_tag_main.find(find).count() == 0):
            return False
        else:
            return True
    def get_once(self,channel_id,tag):
        find = {
            "channel_id":channel_id,
            "tag":tag
        }
        tag_info = self.col_tag_main.find_one(find)
        
        del tag_info["_id"]
        return tag_info

    # 確認條件 True 通過 Flase 失敗
    # day,month,year,total
    def chk_limit(self,channel_id,user_id,tag):
        tag_data = Tags().get_once(channel_id,tag);
        now = datetime.datetime.now();
        find = {
                "channel_id":channel_id,
                "user_id":user_id,
                "tag":tag
            }
        # 如果沒有設定週期
        if 'limit_cycle' in tag_data:
            if tag_data["limit_cycle"] == "none":
                return True
            elif tag_data['limit_cycle'] == 'day':
                day = "{0}-{1}-{2}".format(now.year, now.month, now.day)
                find['datetime'] = day
            elif tag_data['limit_cycle'] == 'month':
                day = "{0}-{1}".format(now.year, now.month)
                find['datetime'] = {"$regex": day}
            elif tag_data['limit_cycle'] == 'year':
                day = "{0}-".format(now.year)
                find['datetime'] = {"$regex": day}
       
            if(self.col_tag_log.find(find).count() >= tag_data['limit_qty']):
                return False
            else:
                return True
        else:
            return True

    # 記錄追蹤
    def set_tag_log(self,channel_id, user_id,tag):
        now = datetime.datetime.now();
        data = {
            "channel_id":channel_id,
            "user_id":user_id,
            'tag':tag,
            "datetime":"{0}-{1}-{2}".format(now.year, now.month, now.day),
            "time":now
        }
        self.col_tag_log.insert_one(data)
        return True

    

    # 取得要被追縱的 tag
    def track_types(self,channel_id,track_types):
        find = {
            "channel_id": channel_id,
            "type":track_types
        }
        datalist = []
        for row in self.col_tag_main.find(find):
            datalist.append(row['tag'])
        
        return list(datalist)
    
    
    def track_types_count(self,channel_id,user_id,t_tags):
        find = {
            "channel_id": channel_id,
            "user_id":user_id,
            "tag":{"$in":t_tags}
        }
        return self.col_tag_log.find(find).count()
    
    # 取得單一日期單一tag用量
    def tags_daily_count(self,channel_id,tag,date):
        find = {
            "channel_id": channel_id,
            "tag":tag,
            "datetime":date
        }
        return self.col_tag_log.find(find).count()

    # 取得標籤所有不重複使用者
    def tag_users(self, channel_id,tag,follow="false"):
        if follow == "true": 
            pipeline = [
                {'$match':{'channel_id':channel_id,'tag':tag,'follow':{'$ne':'unfollow'}}},
                {'$group':{'_id':{"user_id":"$user_id"},"count": { "$sum": 1 }}}
            ]
        else:
           pipeline = [
                {'$match':{'channel_id':channel_id,'tag':tag}},
                {'$group':{'_id':{"user_id":"$user_id"},"count": { "$sum": 1 }}}
            ] 
        users = []
        for i in self.col_tag_log.aggregate(pipeline):
            users.append(i['_id']['user_id'])
        return users
    # 取得所有正常追蹤的 tag 人數
    def all_tags_users(self,channel_id):
        pipeline = [
                {'$match':{'channel_id':channel_id,'follow':{'$ne':'unfollow'}}},
                {'$group':{'_id':{"user_id":"$user_id","tag":"$tag"}}},
                {'$sort':{'_id.tag':-1}}
            ] 
        datalist = []
        for i in self.col_tag_log.aggregate(pipeline):
            datalist.append({
                'tag':i['_id']['tag'],
                'item':1
            })
        # 將資料整理 DataFrame
        p = pd.DataFrame(datalist,columns=['tag','item'])
        res = []
        # 設定 tag 群組 groupby
        for i2 in p.groupby('tag', as_index=False)['item'].count().values.tolist():
            res.append({
                'tag':i2[0],
                'count':i2[1],
            })
        
        return res
    def tag_user_count(self,channel_id,tag):
        pipeline = [
                {'$match':{'channel_id':channel_id,'tag':tag,'follow':{'$ne':'unfollow'}}},
                {'$group':{'_id':{"tag":"$tag"},"count": { "$sum": 1 }}},
                {'$sort':{'_id.tag':-1}}
            ] 
        datalist = []
        for i in self.col_tag_log.aggregate(pipeline):
            return i['count']
        return datalis
    # 取得單一使用者標籤
    def user_tags(self,channel_id,user_id):
        find = {
            "channel_id": channel_id,
            "user_id": user_id
        }
        datalist = []
        for tag in self.col_tag_log.find(find):
            datalist.append(tag['tag'])
        return datalist




