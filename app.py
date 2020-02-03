from flask import Flask, jsonify, request
import json
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


app = Flask(__name__)
client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")


@app.route("/")
def hello():
    return "Hello, World! 3 "



# 單純抓取 webhook 回傳資料
@app.route("/webhook/<channel_id>", methods=["POST", "GET"])
def webhook(channel_id):
    jsondata = request.get_json()
    print(jsondata)
    try:
        jsondata["channel_id"] = channel_id
        event = jsondata["events"][0]
        replyToken = event["replyToken"]
        userId = event["source"]["userId"]
        line_bot_api = LineBotApi(
            'EeW1IZR3U3fYS9rVH1njiVkTlaRUFEvkyXS2xl1swT+p+McTNzdZwZphg1BrjvjTXXcQAlSHK/I2bx2s3Fu8GfUS5tljY2ZO8krNSKgpU6O7GRgwMcxKHfQvp7w4m8PHZZmsGy9C3pf4ifaXws7/+wdB04t89/1O/w1cDnyilFU=')
        line_bot_api.reply_message(replyToken, TextSendMessage(text='Hello World!'))
        line_bot_api.push_message(
            userId, TextSendMessage(text='Hello World! userId'))


    except:
        jsondata = {'data': 'nodata'}
        replyToken = 'null'
    mycol = client.ufs.webhook
    df = pd.DataFrame(jsondata, index=[0])
    mycol.insert_many(df.to_dict('records'))
    return "replyToken"
