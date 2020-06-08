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
from data_model.product import *


class Order:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.col_order = self.client.ufs.order
        self.col_order_log = self.client.ufs.order_log
    
    def get_user_preorder(self,channel_id,user_id):
        find = {
            "channel_id":channel_id,
            "user_id":user_id
        }
        datalist = []
        for data in self.col_order.find(find).sort("datetime",-1):
            del data["_id"]
            datalist.append(data)
        return list(datalist)


    # 各種狀態訂單列表
    # applying pass got fail
    def order_list_by_status(self,channel_id,status):
        find = {
            "channel_id":channel_id,
            "status":status
        }
        
        datalist = []
        for data in self.col_order.find(find).sort("datetime",-1):
            del data["_id"]
            datalist.append(data)
        return list(datalist)
    def order_list_by_product(self,channel_id,product_id,status=""):
        user = User()
        find = {
            "channel_id":channel_id,
            "product_id":product_id
        }
        if status != "":
            find["status"] = status
        
        datalist = []
        for data in self.col_order.find(find).sort("datetime",1):
            del data["_id"]
            data['name'] = user.get_once(data['user_id'],channel_id)['name']
            datalist.append(data)
        
        # print(datalist)
        return list(datalist)


    # 申請預購
    # 2020-06-08 修改為直接扣庫存
    def applying_preorder(self,channel_id,product_id,user_id,qty):
        product = Product()
        p_data = product.get_once(channel_id,product_id)
        user = User()
        now = datetime.datetime.now();
        date_time = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        
        point =  p_data['need_points']
        # 新增預購單
        pre_order = {
            "order_id":str(time.time()),
            "channel_id":channel_id,
            "product_id":product_id,
            "product_img":p_data['product_img'],
            "date_close":p_data['date_close'],
            "date_send":p_data['date_send'],
            "product_name":p_data['product_name'],
            "qty":qty,
            "datetime":date_time,
            "points":point,
            "status":"applying",
            "user_id":user_id,
            "type":p_data['type'],
        }
        self.col_order.insert_one(pre_order)
        # 扣除數量
        product.deduct_qty(channel_id,product_id,qty)
        # 寫入 log
        self.col_order_log.insert_one(pre_order)
        # 扣除點數
        user.deduct_point(user_id,channel_id,point,"預購 {0} ，訂單編號：{1}".format(p_data['product_name'],pre_order['order_id']));
        return pre_order['order_id']
    # 取得訂單資料
    def get_once(self,channel_id,order_id):
        find = {
            "channel_id":channel_id,
            "order_id":order_id
        }
        data = self.col_order.find_one(find)
        del data["_id"]
        return data
    # 確認訂單存在
    def chk_once(self,channel_id,order_id):
        find = {
            "channel_id":channel_id,
            "order_id":order_id
        }
        if self.col_order.find(find).count() == 0:
            return False
        else :
            return True

    def pass_one(self,channel_id,order_id,data):    
        find = {
            "channel_id":channel_id,
            "order_id":order_id
        }
        now = datetime.datetime.now();
        date_time = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        data['pass_datetime'] = date_time
        
        self.col_order.update_one(find,{"$set":data})

        return True
    def order_2_got(self,channel_id,order_id):
        find = {
            "channel_id":channel_id,
            "order_id":order_id,
        }
        now = datetime.datetime.now();
        date_time = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        data = {
            'status':"got",
            "got_datetime":date_time
        }
        self.col_order.update_one(find,{"$set":data})