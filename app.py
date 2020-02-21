#系統元件
from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import json
import pymongo
import pandas as pd
import datetime
from datetime import timedelta
import time
import numpy as np
# line bot 相關元件
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *

from api import *


app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
app.register_blueprint(api)

manager = Manager()

# 登入管理者
@app.route("/login",methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        manager_id = request.values["manager_id"]
        manager_pwd = request.values["manager_pwd"]
        # 先確認目前登入狀態
        if(manager.chk_now() == True):
            return redirect(url_for("channel"))
        else:
            # 如果未登入就去驗證
            if(manager.chk_id_pw(manager_id,manager_pwd) == True):
                # 登入 manager_id
                manager.login(manager_id)
                return redirect(url_for("channel"))
            else:
                flash(manager_id +" 帳號登入失敗，請檢查登入訊息後再重新登入")
                return render_template('login.html')
    else:
        return render_template('login.html')
# 登出
@app.route('/logout', methods=['GET'])
def logout():
    manager.logout()
    return redirect(url_for("login"))


# 首頁＆channel 列表
@app.route("/", methods=["GET", "POST"])
@app.route("/channel", methods=["GET", "POST"])
def channel():
    if(manager.chk_now() == True):
        channel = Channel()
        manager_id = session.get("manager_id")

        if(request.method == "POST"):
            jsondata = {
                "manager_id": manager_id,
                "channel_id":request.values["channel_id"],
                "channel_name":request.values["channel_name"],
                "channel_secret":request.values["channel_secret"],
                "channel_access_token":request.values["channel_access_token"]
            }
            channel.add_once(jsondata)
        datalist = channel.get_list(manager_id)
        return render_template("channel.html",datalist=datalist)
    else:
        return redirect(url_for("login"))

@app.route("/functions", methods=["GET", "POST"])
def functions():
    if(manager.chk_now() == True):
        channel = Channel()
        manager_id = session.get("manager_id")

        return render_template("functions.html")
    else:
        return redirect(url_for("login"))

# 單純抓取 webhook 回傳資料
@app.route("/webhook/<channel_id>", methods=["POST", "GET"])
def webhook(channel_id):
    channel = Channel()
    webhook = Webhook()
    user = User()
    jsondata = request.get_json()
    try:
        
        jsondata["channel_id"] = channel_id
        channel_data = channel.get_channel(channel_id)
        channel_access_token = channel_data["channel_access_token"]
        event = jsondata["events"][0]
        user_id = event["source"]["userId"]
        jsondata["user_id"] = user_id
        webhook.add_log(jsondata)

        # 使用者紀錄
        if(user.chk_once(user_id,channel_id) == True):
            user.set_user_tag(user_id,channel_id,event['type'])
        else :
            user.add_once(user_id,channel_id)
            user.set_user_tag(user_id,channel_id,event['type'])

        # replyToken = event["replyToken"]
        # 回覆
        # line_bot_api = LineBotApi(
        #     'EeW1IZR3U3fYS9rVH1njiVkTlaRUFEvkyXS2xl1swT+p+McTNzdZwZphg1BrjvjTXXcQAlSHK/I2bx2s3Fu8GfUS5tljY2ZO8krNSKgpU6O7GRgwMcxKHfQvp7w4m8PHZZmsGy9C3pf4ifaXws7/+wdB04t89/1O/w1cDnyilFU=')
        # line_bot_api.reply_message(replyToken, TextSendMessage(text='Hello World!'))
        # 主動發送
        
        
        
        

        
        # line_bot_api = LineBotApi(channel_access_token)
        # line_bot_api.push_message(jsondata["user_id"], TextSendMessage(text='Hello World!'+jsondata["user_id"]))


    except (EOFError, KeyboardInterrupt):

        print(EOFError)
        
    # mycol = client.ufs.webhook
    # df = pd.DataFrame(jsondata, index=[0])
    # mycol.insert_many(df.to_dict('records'))
    return "replyToken"


if __name__ == '__main__':
    app.debug = True
    app.run()
