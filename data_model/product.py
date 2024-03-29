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


class Product:
    def __init__(self):
        # self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.client.admin.authenticate('james', 'wolf0719')
        self.col_product = self.client.ufs.product
        self.col_product_categories = self.client.ufs.product_categories

    
    def add_once(self,datajson):
        datajson['update_datetime']= datetime.datetime.now()
        self.col_product.insert_one(datajson)
        return True
    def update_once(self,channel_id,product_id,datajson):
        find = {
            "product_id":product_id,
            "channel_id":channel_id,
        }
        datajson["update_datetime"] =datetime.datetime.now()
        self.col_product.update_one(find,{"$set":datajson})
        return True

    def chk_once(self,channel_id,product_id):
        find = {
            "channel_id":channel_id,
            "product_id":product_id
        }
        if self.col_product.find(find).count() == 0:
            return False
        else:
            return True
    # 確認剩餘量
    def chk_last(self,channel_id,product_id):
        find = {
            "channel_id":channel_id,
            "product_id":product_id
        }
        return self.col_product.find_one(find)['last_qty']
    
   

    def get_list(self,channel_id,category_id=""):
        find = {"channel_id":channel_id}
        if category_id != "":
            find["category_id"] = category_id
        datalist = []
        for d in self.col_product.find(find).sort('update_datetime',-1):
            del d["_id"]
            if 'update_datetime' in d:
                del d["update_datetime"]
            datalist.append(d)
        return list(datalist)
    def product_categories_list(self,channel_id):
        find = {"channel_id":channel_id}
        datalist = []
        for d in self.col_product_categories.find(find).sort("category_id",1):
            del d["_id"]
            del d["channel_id"]
            datalist.append(d)
        return list(datalist)

    def deduct_qty(self,channel_id,product_id,qty):
        last = Product().chk_last(channel_id,product_id);
        last = int(last)-int(qty)
        # 回寫主表
        find = {
            "channel_id":channel_id,
            "product_id":product_id
        }
        self.col_product.update_one(find,{"$set":{"last_qty":last}})
        return True



    def get_once(self,channel_id,product_id):
        find = {
            "channel_id":channel_id,
            "product_id":product_id
        }
        data = self.col_product.find_one(find)
        del data["_id"]
        return data
   