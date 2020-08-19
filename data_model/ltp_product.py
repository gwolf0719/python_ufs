#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

# Model
from data_model.database import *


class Ltp_product:
    def __init__(self):
        self.database = Database();
        self.db = self.database.set_db()
        self.limit_time_point_log = self.db.limit_time_point_log
        self.users = self.db.users
        self.ltp_product = self.db.ltp_product
    
    def chk_product(self,channel_id,product_id):
        find = {
            'channel_id': channel_id,
            'product_id': product_id
        }
        if self.ltp_product.find_one(find) is not None:
            return True
        else:
            return False

    def set_product(self, data):
        if Ltp_product().chk_product(data['channel_id'],data['product_id']) == False:
            self.ltp_product.insert_one(data)
        else:
            find = {
                'channel_id': data['channel_id'],
                'product_id': data['product_id']
            }
            self.ltp_product.update_one(find,{"$set":data})
        return True
    
    def list_product(self,channel_id):
        find = {
            'channel_id': channel_id
        }
        datalist = []
        for d in self.ltp_product.find(find):
            del d["_id"]
            datalist.append(d)
        return list(datalist)

