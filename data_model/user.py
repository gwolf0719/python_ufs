#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
from datetime import datetime
import time
import numpy as np

class User:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.col_user = self.client.ufs.users
        self.col_point_logs = self.client.ufs.point_logs

    # 取得單一帳號資料
    def get_once(self,user_id,channel_id):
        find = {
            "user_id": user_id,
            "channel_id": channel_id
        }
        userdata = self.col_user.find_one(find)
        del userdata["_id"]
        return userdata
    #確認帳號存在
    def chk_once(self, user_id, channel_id):
        find = {
            "user_id": user_id,
            "channel_id": channel_id
        }
        cursor = self.col_user.find(find) 
        if(cursor.count() == 0):
            return False
        else:
            return True
    # 新增使用者
    def add_once(self,user_id,channel_id):
        jsondata = {
            "user_id":user_id,
            "channel_id":channel_id,
            "point":0,
            "created_datetime":datetime.today()
        }
        
        self.col_user.insert_one(jsondata)
        return True

    
    def update_user_main(self,user_id,channel_id,data):
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        self.col_user.update_one(find,{"$set":data})
        return True
    # 設定使用者參數
    def set_user_tag(self,user_id,channel_id,tag):
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        tag = {
            "tag":tag,
            "time":datetime.now(),
            "date":datetime.today()
        }
        self.col_user.update_one(find,{"$push":{"tags":tag}})
        return True
    # 取得使用者有使用到的 TAG
    def get_user_tags(self,user_id,channel_id):
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        user_data = self.col_user.find_one(find)
        res = []
        if "tags" in user_data:
            for t in user_data["tags"]:
                if t['tag'] not in res:
                    res.append(t['tag'])
        return res

    #============================================================================
    #
    # 
    # 點數控制
    #
    # 
    # =================================================================

    # 新增點數
    def add_point(self,user_id,channel_id,point,point_note):
        user_data = User.get_once(self,user_id,channel_id)
        # print(user_data)
        old_point = 0
        if 'point' in user_data:
            old_point = user_data['point']
        new_point = old_point + point
        # 建立 log
        log_data = {
            "user_id":user_id,
            "channel_id":channel_id,
            'original':old_point,
            "point":point,
            "act":"add",
            "update_datetime":datetime.today(),
            "balance_point":new_point,
            "point_note":point_note
        }
        self.col_point_logs.insert_one(log_data)
        # 回寫主表
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        self.col_user.update_one(find,{"$set":{"point":new_point}})
        return new_point


    # 扣除點數
    def deduct_point(self,user_id,channel_id,point,point_note):
        user_data = User.get_once(self,user_id,channel_id)
        old_point = user_data['point']
        new_point = old_point - point
        # 建立 log
        log_data = {
            "user_id":user_id,
            "channel_id":channel_id,
            'original':old_point,
            "point":point,
            "act":"deduct",
            "update_datetime":datetime.today(),
            "balance_point":new_point,
            "point_note":point_note
        }
        self.col_point_logs.insert_one(log_data)
        # 回寫主表
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        self.col_user.update_one(find,{"$set":{"point":new_point}})
        return new_point

    # 取得交易紀錄
    def get_point_logs(self,user_id,channel_id):
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        logs_data = self.col_point_logs.find(find).sort("update_datetime",-1)
        datalist = []
        for row in logs_data:
            del row["_id"]
            datalist.append(row)
        
        return list(datalist)

    




        
