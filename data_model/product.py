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
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.col_product = self.client.ufs.product
        self.col_product_categories = self.client.ufs.product_categories

    
    def add_once(self,datajson):
        self.col_product.insert_one(datajson)
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
        for d in self.col_product.find(find):
            del d["_id"]
            datalist.append(d)
        return list(datalist)
    def product_categories_list(self,channel_id):
        find = {"channel_id":channel_id}
        datalist = []
        for d in self.col_product_categories.find(find):
            del d["_id"]
            del d["channel_id"]
            datalist.append(d)
        return list(datalist)

    def deduct_qty(self,channel_id,product_id,qty):
        last = Product().chk_last(channel_id,product_id);
        last = int(last)-qty
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
   