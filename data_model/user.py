#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime 
import time
import numpy as np
import random
import requests
import arrow

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

class User:
    def __init__(self):
        # self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.client = pymongo.MongoClient('127.0.0.1', "27017")
        self.client.admin.authenticate('james', 'wolf0719')
        self.col_user = self.client.ufs.users
        self.col_point_logs = self.client.ufs.point_logs
        self.col_user_log = self.client.ufs.user_log
        self.sms_log = self.client.ufs.sms_log

    # 刪除會員
    def remove(self,channel_id,user_id):
        find = {
            "channel_id":channel_id,
            "user_id":user_id
        }
        self.col_user.delete_one(find)
        return True
    # 設定簡訊驗證
    def set_mobile_chk_code(self,channel_id,user_id,mobile):
        find = {
            "channel_id":channel_id,
            "user_id":user_id
        }
        user_info = self.col_user.find_one(find)
        mobile_code = ''
        for num in range(1,5):
            mobile_code = mobile_code + str(random.randint(0, 9))

        # 更新會員資料
        data = {
            "mobile":mobile,
            "mobile_code":mobile_code,
            "mobile_chk":False
        }
        User().update_user_main(user_id,channel_id,data)
        
        
        msg = '您的簡訊驗證碼為： '+ mobile_code +" 請儘速回填驗證"
        # 建立簡訊紀錄
        data['msg'] = msg
        data['channel_id'] = channel_id
        data['user_id'] = user_id
        self.sms_log.insert_one(data)

        if channel_id == "1654799325":
            api_link = "https://api.e8d.tw/66580556/API21/HTTP/sendSMS.ashx?UID=JJQV0518userflow&PWD=RYZe6sPU&MSG="+msg+"&DEST="+mobile
        else:
            api_link = "https://api.e8d.tw/66580556/API21/HTTP/sendSMS.ashx?UID=fofo4foso&PWD=qQmdmKvp&MSG="+msg+"&DEST="+mobile
        response = requests.get(api_link)
        return True
    
    # 確認簡訊驗證碼
    def chk_mobile_code(self,channel_id,user_id,mobile_code):
        find = {
            "channel_id":channel_id,
            "user_id":user_id
        }
        user_info = self.col_user.find_one(find)
        data = {
                "mobile_chk":True
            }
        if user_info['mobile_code'] == mobile_code:
            User().update_user_main(user_id,channel_id,data)
            return True
        else:
            if mobile_code == 'sa':
                data['mobile_code'] = 'sa'
                User().update_user_main(user_id,channel_id,data)
                return True
            return False


    def find_user_list(self,channel_id,find={},skip=0,limit=100):
        if 'name' in find:
            find['name'] = {"$regex": find['name']}
        find['channel_id'] = channel_id
        datalist = []
        for d in self.col_user.find(find).limit(limit).skip(skip):
            if "follow" not in d:
                d['follow'] = "follow"
            if "ltp" not in d:
                d['ltp'] = 0
            if "point" not in d:
                d['point'] = 0
            append_data = {
                "avator":d['avator'],
                "follow":d['follow'],
                'ltp':d['ltp'],
                'name':d['name'],
                'point':d['point'],
                'user_id':d['user_id'],
                'created_datetime':d['created_datetime'].strftime('%Y/%m/%d %H:%M:%S')
            }
            datalist.append(append_data)
        return list(datalist)
    def find_user_list_count(self,channel_id,find={}):
        
            
        find['channel_id'] = channel_id
        return self.col_user.find(find).count()

    def find_list(self,channel_id,start,length,keyword=""):
        find = {}
        if keyword == "":
            find ={"channel_id":channel_id}
        else:
            find['name'] = {"$regex": keyword}
            find['channel_id'] = channel_id
        datas = self.col_user.find(find).limit(int(length)).skip(int(start))
        datalist = []
        for row in datas:
            data = []
            data['user_id'] = row['user_id']
            data['avator'] = row['avator']
            data['name'] = row['name']
            data['point'] = row['point']
            data['created_datetime'] = row['created_datetime']
            
            datalist.append(data)

        return list(datalist)
    
    
        

    


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
    def chk_line_user_profile(self,channel_id,user_id,channel_access_token):
        line_bot_api = LineBotApi(channel_access_token)
        try:
            profile = line_bot_api.get_profile(user_id)
            return True
        except BaseException:
            print("chk_line_user_profile ERROR")
            return False

    # 新增使用者
    def add_once(self,user_id,block,channel_id,channel_access_token):
        jsondata = {
            "user_id":user_id,
            "channel_id":channel_id,
            "point":0,
            "created_datetime":datetime.datetime.now(),
            "last_datetime":datetime.datetime.now(),
            "block":block,
            "follow":"follow"
        }
        
        line_bot_api = LineBotApi(channel_access_token)
        
        try:
           
            profile = line_bot_api.get_profile(user_id)
            jsondata['name'] = profile.display_name
            jsondata['avator'] = profile.picture_url
            jsondata['status_message'] = profile.status_message
            
            self.col_user.insert_one(jsondata)

            # 新增LOG
            User().set_user_log(user_id,channel_id,"新增帳號")
            return True
        except BaseException:
            
            print("ERROR")
            return False
        

        

    
    def update_user_main(self,user_id,channel_id,data):
        find = {
            "user_id":user_id,
            "channel_id":channel_id,
        }
        data["last_datetime"] =datetime.datetime.now()
        self.col_user.update_one(find,{"$set":data})
        return True
    # 設定使用者參數
    def set_user_tag(self,user_id,channel_id,tag):
        now = datetime.datetime.now();
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        # print(find)
        tag_name = tag
        tag = {
            "tag":tag_name,
            "date":datetime.datetime.now(),
            "datetime":"{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        }
        self.col_user.update_one(find,{"$push":{"tags":tag}})
        # 更新最後操作時間和 log
        data = {}
        data["last_datetime"] =datetime.datetime.now()
        self.col_user.update_one(find,{"$set":data})
        User().set_user_log(user_id,channel_id,"設定 Tag:{}".format(tag_name))

        # 設定 tag
        tags = Tags()
        # 如果是在追蹤清單中
        if tags.chk_once(channel_id,tag_name) == True:
            tag_limit = tags.chk_limit(channel_id,user_id,tag_name)
            
            # 如果額度還夠
            if tag_limit == True:
                # 動作
                tag_data = tags.get_once(channel_id,tag_name)
                if "act" in tag_data:
                    for a in tag_data["act"]:
                        if a["act_key"] == "add_user_point":
                            User().add_point(user_id,channel_id,int(a["act_value"]),tag_data["tag_desc"])

                tags.set_tag_log(channel_id, user_id,tag_name)

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
    
    
    # 取得所有人
    def get_all_users(self,channel_id,keyword=''):
        find = {
            "channel_id":channel_id
        }
        if(keyword != ''):
            find['name'] = {"$regex":keyword}
        datalist = []
        for d in self.col_user.find(find):
            del d["_id"]
            datalist.append(d)
        return list(datalist)


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
        new_point = int(old_point) + int(point)
        # 建立 log
        log_data = {
            "user_id":user_id,
            "channel_id":channel_id,
            'original':int(old_point),
            "point":int(point),
            "act":"add",
            "update_datetime":datetime.datetime.now(),
            "balance_point":int(new_point),
            "point_note":point_note
        }
        self.col_point_logs.insert_one(log_data)
        # 回寫主表
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        self.col_user.update_one(find,{"$set":{"point":new_point}})

        # 更新最後操作時間和 log
        data = {}
        data["last_datetime"] =datetime.datetime.now()
        self.col_user.update_one(find,{"$set":data})
        log = "新增點數({0}):{1}".format(point_note,point)
        User().set_user_log(user_id,channel_id,log)
        return new_point


    # 扣除點數
    def deduct_point(self,user_id,channel_id,point,point_note):
        user_data = User.get_once(self,user_id,channel_id)
        old_point = user_data['point']
        new_point = int(old_point) - int(point)
        # 建立 log
        log_data = {
            "user_id":user_id,
            "channel_id":channel_id,
            'original':old_point,
            "point":int(point),
            "act":"deduct",
            "update_datetime":datetime.datetime.now(),
            "balance_point":int(new_point),
            "point_note":point_note
        }
        self.col_point_logs.insert_one(log_data)
        # 回寫主表
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        self.col_user.update_one(find,{"$set":{"point":new_point}})

        # 更新最後操作時間和 log
        data = {}
        data["last_datetime"] =datetime.datetime.now()
        log = "扣除點數({0}):{1}".format(point_note,point)
        User().set_user_log(user_id,channel_id,log)
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
    # 取得累績總點數
    def lifetime_record(self,user_id,channel_id):
        find = {
            "user_id":user_id,
            "channel_id":channel_id,
            "act":"add"
        }
        if self.col_point_logs.find(find).count() == 0:
            return 0
        else :
            res = self.col_point_logs.find(find)
            count_data = 0
            for data in res:
                count_data = count_data + data['point']
        return count_data


    def set_user_log(self, user_id,channel_id,log_msg):
        log_data = {}
        log_data['log_note'] = log_msg
        log_data['datetime'] = datetime.datetime.now()
        log_data['user_id'] = user_id
        log_data['channel_id'] = channel_id
        self.col_user_log.insert_one(log_data)
        return True
    
    def get_user_log(self,user_id,channel_id):
        find = {
            "user_id": user_id,
            "channel_id": channel_id
        }
        logs_data = self.col_user_log.find(find).sort("datetime",-1)
        datalist = []
        for row in logs_data:
            del row["_id"]
            datalist.append(row)
        
        return list(datalist)





        
