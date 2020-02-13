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
            "points":0,
            "created_datetime":datetime.today()
        }
        
        self.col_user.insert_one(jsondata)
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
    def update_user_main(self,user_id,channel_id,data):
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        
        self.col_user.update_one(find,{"$set":data})
        return True


        
