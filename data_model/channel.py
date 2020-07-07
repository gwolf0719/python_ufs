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

class Channel:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.col_channel = self.client.ufs.channel
        self.col_manager = self.client.ufs.manager
    # 取得 manager_id 所屬的 channel
    def get_list(self,manager_id):
        mycol = self.col_manager
        find = {"manager_id":manager_id}
        # datas = mycol.find(find).sort("create_datetime",-1)
        data = mycol.find_one(find)
        datalist = []
        for d in data['channels']:
            datalist.append({
                "channel_id":d["channel_id"],
                "channel_name":d["channel_name"],
                "level":d['level']
            })
        return list(datalist)
    # 新增 Channel 
    def add_once(self,jsondata):
        mycol = self.client.ufs.channel
        df = pd.DataFrame(jsondata, index=[0])
        mycol.insert_many(df.to_dict('records'))
        return True

    # 取得單一 channel 資料
    def get_channel(self, channel_id):
        mycol = self.client.ufs.channel
        find = {"channel_id":channel_id}
        data = mycol.find_one(find)
        return data
    # 取得單一 channel 資料
    def get_channel_manger(self, channel_id,manager_id):
        mycol = self.col_manager
        find = {"manager_id":manager_id}
        data = mycol.find_one(find)
        res_data = []
        for item in data['channels']:
            if item['channel_id'] == channel_id :
                res_data = item
            
        return res_data

    def chk_once(self,channel_id):
        find = {"channel_id":channel_id}
        if(self.col_channel.find(find).count() == 0):
            return False
        else:
            return True

