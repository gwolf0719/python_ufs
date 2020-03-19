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

class Webhook:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
    
    def add_log(self,jsondata):
        # 記錄原始得到資料
        webhook_log = self.client.ufs.webhook_log
        webhook_log.insert_one(jsondata)
        # df = pd.DataFrame(jsondata, index=[0])
        # webhook_log.insert_many(df.to_dict('records'))
        

        return True
