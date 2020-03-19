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
    
    # 寫入 chat
    def add_chat(self,chat_data):
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
                'user_id':chat_data['user_id'],
                'name':chat_data['user_id'],
                'read_status':0,
                'avator':chat_data['avator']
            }
            self.col_chat_room.insert_one(room_data)


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
        data = self.col_chat_room.find({"channel_id":channel_id}).sort("_id",1)
        datalist = []
        for row in data:
            del row["_id"]
            datalist.append(data)
        return list(datalist)
    
    
        
    # 確認聊天室
    def chk_chat_room(self,channel_id,user_id):
        find = {'channel_id':channel_id,'user_id':user_id}
        if self.col_chat_room.find(find).count() == 0:
            return False
        else:
            return True
    # 刪除聊天室
    # 設定聊天室已讀狀態
    def set_chat_room_read(self,channel_id,user_id,read_status):
        match = {'channel_id':channel_id,'user_id':user_id}
        set_data = {"$set":{'read_status':read_status}}
        self.col_chat_room.find(match,set_data)
        return True
    # def get_chat_room(self,channel_id):
        
    #     user = User()
    #     match = {'channel_id':channel_id}
    #     group = {
    #         '_id': {'user_id':'$user_id','name':'$name','avatar':'$avatar'},
    #         # 'user_id':{'user_id':'$user_id'}
    #     }
       
    #     collection = self.col_chat.aggregate([{'$match': match},{'$group': group}])
    #     datalist = []
    #     for row in collection:
    #         user_id = row["_id"]['user_id']
    #         not_read_count = Chat().get_not_read(channel_id,user_id)
    #         user_chat = Chat().get_user_chat(channel_id,user_id)
    #         room = {
    #             'user_id':user_id,
    #             'name':user_chat[-1]['name'],
    #             'not_read_count':not_read_count,
    #             'avator':user_chat[-1]['avator'],
    #             'datetime':user_chat[-1]['datetime'],
    #         }

    #         datalist.append(room)
        # return datalist