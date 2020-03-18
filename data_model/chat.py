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

class Chat:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.col_chat = self.client.ufs.chat
    
    # 寫入 chat
    def add_chat(self,chat_data):
        now = datetime.datetime.now();
        chat_data['datetime'] = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        self.col_chat.insert_one(chat_data)
        return True
    # 取得所有聊天室
    def get_chat_room(self,channel_id):
        
        user = User()
        match = {'channel_id':channel_id}
        group = {
            '_id': {'user_id':'$user_id','name':'$name','avatar':'$avatar'},
            # 'user_id':{'user_id':'$user_id'}
        }
       
        collection = self.col_chat.aggregate([{'$match': match},{'$group': group}])
        datalist = []
        for row in collection:
            user_id = row["_id"]['user_id']
            not_read_count = Chat().get_not_read(channel_id,user_id)
            user_chat = Chat().get_user_chat(channel_id,user_id)
            room = {
                'user_id':user_id,
                'name':user_chat[0]['name'],
                'not_read_count':not_read_count,
                'avator':user_chat[0]['avator'],
                'datetime':user_chat[0]['datetime'],
            }

            datalist.append(room)
        return datalist
    def get_not_read(self,channel_id,user_id):
        match = {'channel_id':channel_id,'user_id':user_id,'read_status':0}
        count = self.col_chat.find(match).count()
        return count

    def get_user_chat(self, channel_id, user_id):
        find = {'channel_id':channel_id,'user_id':user_id}
        data = self.col_chat.find(find).sort('_id',-1)
        datalist = []
        for row in data:
            del row['_id']
            datalist.append(row)
        return list(datalist)