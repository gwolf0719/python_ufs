#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

class Webhook:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
    
    def add_log(self,jsondata):
        mycol = self.client.ufs.webhook
        df = pd.DataFrame(jsondata, index=[0])
        mycol.insert_many(df.to_dict('records'))
        return True
