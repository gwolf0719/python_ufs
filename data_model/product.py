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

    
    def add_once(self,datajson):
        self.col_product.insert_one(datajson)
        return True

    def get_list(self,channel_id):
        find = {"channel_id":channel_id}
        datalist = []
        for d in self.col_product.find(find):
            del d["_id"]
            datalist.append(d)
        return list(datalist)

    # def get_once(self,msg_id):
    #     find = {"msg_id": msg_id}
    #     msg = self.col_msg.find_one(find)
    #     del msg["_id"]
    #     return msg
   