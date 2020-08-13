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
        self.col_product = self.client.ufs.product
    
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

    # 取得消費單一商品清單
    def user_product_orders(self,channel_id, user_id,product_id):
        find = {
            "channel_id":channel_id,
            "user_id":user_id,
            "product_id":product_id,
            "status":{"$ne":"cancel"}
        }
        datalist = []
        for data in self.col_order.find(find).sort("datetime",-1):
            del data["_id"]
            datalist.append(data)
        return list(datalist)


    def cancel_order(self,channel_id,order_id):
        find = {
            "channel_id":channel_id,
            "order_id":order_id
        }
        now = datetime.datetime.now();
        date_time = "{0}-{1}-{2} {3}:{4}:{5}".format(now.year, now.month, now.day,now.hour,now.minute,now.second)
        data = {
            'cancel_datetime':date_time,
            'status':"cancel"
        }
        
        self.col_order.update_one(find,{"$set":data})



    # 重新計算剩餘量
    def rechk_last_product(self,channel_id):
        # 找出所有未取消的單
        pipeline = [
            {
                "$match":{"channel_id":channel_id,"status":{"$ne":"cancel"}}
            },{
                "$group":{
                    "_id":"$product_id", "total":{"$sum":1}
                }
            }]
        datalist = []
        for data in self.col_order.aggregate(pipeline):
            f = {
                "channel_id":channel_id,
                "product_id":data['_id']
            }
            # print(f)
            p = self.col_product.find_one(f)
            if p != None:
                
                # 計算剩餘數量
                last_qty  = int(p['total_qty']) - int(data['total'])
                update_data = {
                    "last_qty":last_qty
                }
                self.col_product.update_one(f,{"$set":update_data})
    def rechk_last_product_once(self,channel_id,product_id):
        #取得商品
        f = {
                "channel_id":channel_id,
                "product_id":product_id
            }
        p = self.col_product.find_one(f)
        #取得正常的交易量
        pipeline = [
            {
                "$match":{"channel_id":channel_id,"product_id":product_id,"status":{"$ne":"cancel"}}
            },{
                "$group":{
                    "_id":"$product_id", "total":{"$sum":1}
                }
            }]
        t = 0
        datalist = self.col_order.aggregate(pipeline)

        for data in datalist:
            print(data)
            t = int(t) + int(data['total'])
        print(t)

        total = int(p['total_qty'])-t
        return total

    # 各種狀態訂單列表
    # 訂單總表
    def order_list(self,channel_id):
        user = User()
        find = {
            "channel_id":channel_id
        }
        datalist = []
        for data in self.col_order.find(find).sort("datetime",-1):
            del data["_id"]
            userdata = user.get_once(data['user_id'],channel_id)
            data['name'] = userdata['name']
            datalist.append(data)
        return list(datalist)

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
    
    # 針對商品篩選訂單
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