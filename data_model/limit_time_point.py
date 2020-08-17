#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

# Model
from data_model.database import *

class limit_time_point:
    def __init__(self):
        database = Database();
        self.limit_time_point_log = database.set_doc('limit_time_point_log')
    
    # 確認使用者點數餘額
    def chk_once(self,channel_id,user_id):
        find = {
            "user_id":user_id,
            "channel_id":channel_id,
            "act":"add"
        }
        pipeline = [
            {'$match':find},
            {'$group': {'_id': "$user_id", 'point': {'$sum': '$point'}}},
        ]
        if self.limit_time_point_log.find(find).count() == 0:
            return 0
        else :
            res = self.limit_time_point_log.aggregate(pipeline)
            print(res[0])
            for data in res:
                print(data)
        return data['point']

