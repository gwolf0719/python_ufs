#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *
from data_model.tags import *

class Webhook:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.col_tag_log = self.client.ufs.tag_log

    # 記錄原始得到資料
    def add_log(self,jsondata):
        
        webhook_log = self.client.ufs.webhook_log
        df = pd.DataFrame(jsondata, index=[0])
        webhook_log.insert_many(df.to_dict('records'))
        return True

    # 設定這個使用者的追蹤狀態
    def setfollow(self,channel_id,jsondata):
        event = jsondata["events"][0]
        user_id = event["source"]["userId"]
        follow_status = ''
        if event['type'] == 'follow':
            follow_status = "follow"
        elif event['type'] == 'unfollow':
            follow_status = "unfollow"
        else:
            follow_status = ''

        if follow_status != '':
            # 更新會員資料
            data = {
                "follow":follow_status
            }
            User().update_user_main(user_id,channel_id,data)
            # {"channel_id":"1654478468","user_id":"U5cf4ced528d4274f11a84514e67b6bc4"},,false,true
            find = {"channel_id":channel_id,"user_id":user_id}
            setdata = {'$set':{"follow":follow_status}}
            self.col_tag_log.update(find,setdata,false,true)

        return True


