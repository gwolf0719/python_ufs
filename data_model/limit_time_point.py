#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

# Model
from data_model.database import *

class Limit_time_point:
    def __init__(self):
        self.database = Database();
        self.db = self.database.set_db()
        self.limit_time_point_log = self.db.limit_time_point_log
        self.users = self.db.users
    
    def user_point_log(self,channel_id,user_id,act):
        find = {
            "channel_id":channel_id,
            "user_id":user_id,
            "act":act
        }
        datalist = []
        for d in self.limit_time_point_log.find(find).sort('created_datetime',-1):
            del d['_id']
            datalist.append(d)
        return list(datalist)

    

    def user_point_info(self,channel_id,user_id):
        res = {
            "add":Limit_time_point().chk_user_add_total(channel_id, user_id),
            "consume":Limit_time_point().chk_user_consume_total(channel_id, user_id),
        }
        # 計算總數
        res["total"] = int(res['add'])- int(res['consume'])
        # 回寫會員主表
        data = {}
        find = {
            "user_id":user_id,
            "channel_id":channel_id
        }
        data["last_datetime"] =datetime.datetime.now()
        data["ltp"] = res['total']
        self.users.update_one(find,{"$set":data})
        # 取得下個月即將消失的點數
        return res

    # 點數異動  act = add ,consume
    def ch_point(self,channel_id,user_id,point,note,act,limit=''):
        
        data = {
            "user_id":user_id,
            "channel_id":channel_id,
            "point":int(point),
            "note":note,
            "act":act,
            "limit":limit
        }
        data["update_datetime"] =datetime.datetime.now()
        self.limit_time_point_log.insert_one(data)
        return True

    # 取得下個月即將消失的點數
    # 累計到到期日前的總點數 - 總消費點數
    def get_month_last(self,limit,channel_id,user_id):
        # 到到期日前的總點數 
        add = Limit_time_point().chk_user_add_total(channel_id,user_id,limit)
        last_point = add - Limit_time_point().chk_user_consume_total(channel_id,user_id)
        return last_point


    

    # 確認使用者累計增加總點數 =============
    def chk_user_add_total(self,channel_id,user_id,limit=''):
        find = {
            "user_id":user_id,
            "channel_id":channel_id,
            "act":"add"
        }
        if limit != '':
            find['limit'] = {"$lte":limit}
        pipeline = [
            {'$match':find},
            {'$group': {'_id': "$user_id", 'point': {'$sum': '$point'}}},
        ]
        if self.limit_time_point_log.find(find).count() == 0:
            return 0
        else :
            res = self.limit_time_point_log.aggregate(pipeline)
            for data in res:
                point = data['point']
        return point
    # 確認使用者累計消費總點數 =============
    def chk_user_consume_total(self,channel_id,user_id):
        find = {
            "user_id":user_id,
            "channel_id":channel_id,
            "act":"consume"
        }
        pipeline = [
            {'$match':find},
            {'$group': {'_id': "$user_id", 'point': {'$sum': '$point'}}},
        ]
        if self.limit_time_point_log.find(find).count() == 0:
            return 0
        else :
            res = self.limit_time_point_log.aggregate(pipeline)
            for data in res:
                point = data['point']
        return point

