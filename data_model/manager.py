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

class Manager:
    def __init__(self):
        # self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.client.admin.authenticate('james', 'wolf0719')
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
        # print(session.get("manager_id"))
    # 登出
    def logout(self):
        session.clear()