#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
from datetime import datetime
import time
import numpy as np

class Msg:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.col_msg = self.client.ufs.msgs

    def add_once(self,datajson):
        datajson['manager_id']  = session.get("manager_id")
        datajson['msg_id']  = str(round(time.time()))
        datajson["created_datetime"] = datetime.today()
        self.col_msg.insert_one(datajson)
        return True

    def get_list(self,msg_type=None):
        find = {}
        if msg_type is not None:
            find = {
                "msg_type":msg_type
            }
        find["channel_id"] = session.get("channel_id")
        msgs = self.col_msg.find(find).sort("created_datetime",-1)
        
        datalist = []
        for d in msgs:
            datalist.append(d)
        return list(datalist)

    def get_once(self,msg_id):
        find = {"msg_id": msg_id}
        msg = self.col_msg.find_one(find)
        del msg["_id"]
        return msg





