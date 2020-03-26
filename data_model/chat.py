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
        self.col_chat_room = self.client.ufs.chat_room
        self.col_auto_reply = self.client.ufs.auto_reply
    
    # 寫入 chat
    def add_chat(self,chat_data):
        print(chat_data['channel_id'])
        print(chat_data['user_id'])
        now = datetime.datetime.now();
        chat_data['datetime'] = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        self.col_chat.insert_one(chat_data)

        # 判斷聊天室存在
        if Chat().chk_chat_room(chat_data['channel_id'],chat_data['user_id']) == True:
            # 如果發話者是 user 則設定未讀
            if chat_data['originator'] == 'user':
                print("如果發話者是 user 則設定未讀")
                Chat().set_chat_room_read(chat_data['channel_id'],chat_data['user_id'],0)
            else:
                print("如果發話者是 admin 則設定已讀")
                Chat().set_chat_room_read(chat_data['channel_id'],chat_data['user_id'],1)
        # 否則直接建立
        else:
            room_data = {
                'channel_id':chat_data['channel_id'],
                'user_id':chat_data['user_id'],
                'name':chat_data['name'],
                'read_status':0,
                'avator':chat_data['avator']
            }
            # self.col_chat_room.insert_one(room_data)
            Chat().open_chat_room(room_data)


        return chat_data['datetime']
    
    def get_not_read(self,channel_id,user_id):
        match = {'channel_id':channel_id,'user_id':user_id,'read_status':0}
        count = self.col_chat.find(match).count()
        return count

    def get_user_chat(self, channel_id, user_id):
        find = {'channel_id':channel_id,'user_id':user_id}
        data = self.col_chat.find(find).sort('_id',1)
        datalist = []
        for row in data:
            del row['_id']
            
            if 'text' in row:
                row['text'] = row['text'].replace('\n','<br>')
            datalist.append(row)
        return list(datalist)

    def set_read(self,channel_id,user_id):
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        
        self.col_chat.update_many(find,{"$set":{"read_status":1}})
        # print("ok")
        return True

    ########################################################################
    #
    #聊天室
    #######################
    # 取得所有聊天室
    def get_chat_room(self,channel_id):
        data = self.col_chat_room.find({"channel_id":channel_id})
        
        datalist = []
        for row in data:
            del row['_id']
            datalist.append(row)
        return list(datalist)
    
    # 打開聊天室
    def open_chat_room(self,room_data):
        self.col_chat_room.insert_one(room_data)
        return True

    
    # 確認聊天室
    def chk_chat_room(self,channel_id,user_id):
        find = {'channel_id':channel_id,'user_id':user_id}
        if self.col_chat_room.find(find).count() == 0:
            return False
        else:
            return True
    # 刪除聊天室
    def remove_chat_room(self,channel_id,user_id):
        find = {'channel_id':channel_id,'user_id':user_id}
        self.col_chat_room.delete_one(find)
        return True
    # 設定聊天室已讀狀態
    def set_chat_room_read(self,channel_id,user_id,read_status):
        match = {'channel_id':channel_id,'user_id':user_id}
        set_data = {"$set":{'read_status':read_status}}
        self.col_chat_room.update_one(match,set_data)
        return True
    
##############################################
## 自動回覆 
##############################################
    # 確認自動回覆存在
    def chk_auto_reply(self,channel_id):
        find = {"channel_id":channel_id}
        print(find)
        if self.col_auto_reply.find(find).count() == 0:
            return False
        else :
            return True
    # 更新自動回覆
    def update_auto_reply(self,channel_id,json_data):
        find = {"channel_id":channel_id}
        set_data = {"$set":json_data}
        self.col_auto_reply.update_one(find,set_data)
        return True
    # 新增自動回覆
    def add_auto_reply(self,json_data):
        self.col_auto_reply.insert_one(json_data)
        return True
    # 取得自動回覆
    def get_auto_reply(self,channel_id):
        find = {"channel_id":channel_id}
        data = self.col_auto_reply.find_one(find)
        del data["_id"]
        return data

    # 判斷無人執守時間
    # 回傳 False 表示不做動
    def chk_auto_reply_time(self,channel_id):
        # 確認規則存在
        if Chat().chk_auto_reply(channel_id) == False:
            print("a1")
            return False
        # 確認啟動狀態
        auto_reply = Chat().get_auto_reply(channel_id)
        if auto_reply['switch'] == 0:
            print("a2")
            return False
        
        print("a")
        today_week_day = datetime.date.today().weekday()
        today_cycle = auto_reply['cycle'][today_week_day]


        n_time = datetime.datetime.now()
        start_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+today_cycle['start'], '%Y-%m-%d%H:%M')
        end_time1 =  datetime.datetime.strptime(str(datetime.datetime.now().date())+today_cycle['end'], '%Y-%m-%d%H:%M')
        
        if n_time > start_time and n_time < end_time1:
            # 聊天時間
            return False
        else:
            # 機器人時間
            return auto_reply['text_info']

