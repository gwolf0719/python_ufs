#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
from datetime import datetime
import time
import numpy as np

# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *
from data_model.tags import *
from data_model.product import *


class order:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.col_order = self.client.ufs.order
        self.col_order_log = self.client.ufs.col_order_log
    
    # 申請預購
    def applying_preorder(self,channel_id,product_id,user_id):
        product = Product()
        qty = 1
        p_data = product.get_once(channel_id,product_id)
        user = User()
        now = datetime.datetime.now();
        datetime = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        
        point =  p_data['neet_poionts']
        # 新增預購單
        pre_order = {
            "channel_id":channel_id,
            "product_id":product_id,
            "product_name":p_data['product_name'],
            "qty":qty,
            "datetime":datetime,
            "points":point,
            "status":"applying",
            "user_id":user_id
        }
        self.col_order.insert_one(pre_order)
        # 扣除數量
        
        # 扣除點數
        user.deduct_point(user_id,channel_id,point,"預購 {0} ".format(p_data['product_name'])):