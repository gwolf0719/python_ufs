#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

class Manager:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
    # 確認目前登入狀態
    def chk_now(self):
        if session.get("manager_id") is None:
            return False
        else:
            return True
    # 取得單一帳號資料
    def get_once(self,manager_id):
        manager = self.client.ufs.manager
        manager_data = manager.find_one({"manager_id":manager_id})
        return manager_data
    # 驗證帳密正確性
    def chk_id_pw(self,manager_id,manager_pwd):
        manager_data = Manager.get_once(self,manager_id)
        if(manager_data["manager_pwd"] == manager_pwd):
            return True
        else:
            return False
    

    # 登入
    def login(self,manager_id):
        session["manager_id"] = manager_id
    # 登出
    def logout(self):
        session['manager_id'] = False
        


    # 宣告資料庫和資料表
        # manager = self.client.thermometer.thermometer_mac
        # cursor = mycol.find({'mac_id': mac_id})
        # count_result = cursor.count()
        # if(count_result == 0):
        #     return False
        # else:
        #     return True

    # 確認帳號密碼正確