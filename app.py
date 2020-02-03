from flask import Flask, jsonify, request
import json
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")


@app.route("/")
def hello():
    return "Hello, World! 3 "


@app.route("/webhook/<channel_id>", methods=["POST", "GET"])
def webhook(channel_id):
    
    try:
        jsondata = request.get_json()
        jsondata["channel_id"] = channel_id
    except:
        jsondata = {'data': 'nodata'}
    
    mycol = client.ufs.webhook
    
    df = pd.DataFrame(jsondata, index=[0])
    mycol.insert_many(df.to_dict('records'))

    return channel_id
