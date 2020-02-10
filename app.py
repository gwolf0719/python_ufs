from flask import Flask, jsonify, request, render_template,session,redirect,url_for
import os
import json
import pymongo
import pandas as pd
import datetime
from datetime import timedelta
import time
import numpy as np

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


from data_model.manager import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
client = pymongo.MongoClient("mongodb://james:wolf0719@cluster0-shard-00-01-oiynz.azure.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")

manager = Manager()

@app.route("/login",methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        manager_id = request.values["manager_id"]
        manager_pwd = request.values["manager_pwd"]
        
        
        # 先確認目前登入狀態
        if(manager.chk_now() == True):
            return "login done"+session.get("manager_id")
        else:
            # 如果未登入就去驗證
            if(manager.chk_id_pw(manager_id,manager_pwd) == True):
                manager.login(manager_id)
                return "login doing"+session.get("manager_id")
            else:
                return "login failed"
    else:
        return render_template('login.html')
@app.route('/logout', methods=['GET'])
def logout():
    
    manager.logout()
    return redirect(url_for("login"))

# 單純抓取 webhook 回傳資料
@app.route("/webhook/<channel_id>", methods=["POST", "GET"])
def webhook(channel_id):
    jsondata = request.get_json()
    try:
        jsondata["channel_id"] = channel_id
        event = jsondata["events"][0]
        replyToken = event["replyToken"]
        # 回覆
        line_bot_api = LineBotApi(
            'EeW1IZR3U3fYS9rVH1njiVkTlaRUFEvkyXS2xl1swT+p+McTNzdZwZphg1BrjvjTXXcQAlSHK/I2bx2s3Fu8GfUS5tljY2ZO8krNSKgpU6O7GRgwMcxKHfQvp7w4m8PHZZmsGy9C3pf4ifaXws7/+wdB04t89/1O/w1cDnyilFU=')
        line_bot_api.reply_message(replyToken, TextSendMessage(text='Hello World!'))
        # 主動發送
        userId = event["source"]["userId"]
        line_bot_api.push_message(
            userId, TextSendMessage(text='Hello World! userId'))


    except:
        jsondata = {'data': 'nodata'}
        replyToken = 'null'
        
    mycol = client.ufs.webhook
    df = pd.DataFrame(jsondata, index=[0])
    mycol.insert_many(df.to_dict('records'))
    return "replyToken"


if __name__ == '__main__':
    app.debug = True
    app.run()
