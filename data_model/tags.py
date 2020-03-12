#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
from datetime import datetime
import time
import numpy as np


class Tags:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.col_tag_main = self.client.ufs.tag_main
        self.col_tag_log = self.client.ufs.tag_log

    # 新增標籤主表資料
    # ===============================
    # tag_data = {
    #    channel_id:
    #    tag:
    #    tag_desc:
    #    limit_cycle:
    #    limit_qty:
    #    act:{
    #            act_key:
    #            act_value:
    #       }    
    # }
    def set_tag_main(self,tag_data):
        self.col_tag_main.insert_one(tag_data)
        return True
    # 取得所有追縱標籤資料
    def get_tag_list(self,channel_id):
        find = {
            "channel_id": channel_id
        }
        datalist = []
        for row in self.col_tag_main.find(find):
            del row["_id"]
            datalist.append(row)
        return list(datalist)
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
        # print(find)
        tag_info = self.col_tag_main.find_one(find)
        # print(tag_info)
        del tag_info["_id"]
        return tag_info

    # 確認條件 True 通過 Flase 失敗
    # day,month,year,total
    def chk_limit(self,channel_id,user_id,tag):
        tag_data = Tags().get_once(channel_id,tag);
        now = datetime.now();
        find = {
                "channel_id":channel_id,
                "user_id":user_id,
                "tag":tag
            }

        if tag_data["limit_cycle"] == "none":
            return True
        elif tag_data['limit_cycle'] == 'day':
            day = "{0}-{1}-{2}".format(now.year, now.month, now.day)
            find['datetime'] = day
        elif tag_data['limit_cycle'] == 'month':
            day = "{0}-{1}".format(now.year, now.month)
            find['datetime'] = {"$regex": day}
        elif tag['limit_cycle'] == 'year':
            day = "{0}-".format(now.year)
            find['datetime'] = {"$regex": day}
       
        if(self.col_tag_log.find(find).count() > tag_data['limit_qty']):
            return False
        else:
            return True

    # 記錄追蹤
    def set_tag_log(self,channel_id, user_id,tag):
        now = datetime.now();
        data = {
            "channel_id":channel_id,
            "user_id":user_id,
            'tag':tag,
            "datetime":"{0}-{1}-{2}".format(now.year, now.month, now.day)
        }
        self.col_tag_log.insert_one(data)
        return True


    # 執行動作
    # def do_tag_act(self,channel_id,user_id,tag):

