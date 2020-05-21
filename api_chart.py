from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import re
import json
import pymongo
import pandas as pd
import datetime 
import time
import numpy as np

api_chart = Blueprint('api_chart', __name__)


db = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")

# 新註冊人口
@api_chart.route('/api_chart/new_reg/<channel_id>/<start>/<end>')
def set_channel(channel_id,start,end):
    # 搜尋區間資料
    users = db.ufs.users.find(
        {
            "created_datetime":{
                "$gte" : datetime.datetime(int(start.split("-")[0]), int(start.split("-")[1]), int(start.split("-")[2])),
                "$lt": datetime.datetime(int(end.split("-")[0]), int(end.split("-")[1]), int(end.split("-")[2]))
            },
            "channel_id":channel_id
        }
    )
    datalist = []
    for row in users:
        del row["_id"]
        datalist.append(row)
    # 將資料轉成 DataFrame
    df = pd.DataFrame(datalist)
    df = df.set_index('created_datetime', inplace = False)
    # 設定每日數量統計
    df2 = df.resample('D')["user_id"].count()

    # print(df2)

    # 製作 data list
    d_list = []
    for d in df2.values:
        d = int(d)
        d_list.append(d)
    # 製做 index list
    i_list =[]
    for i in df2.index:
        i = str(i)
        i = i.split(' ')
        i_list.append(i[0])

    json_data = {'sys_code':"200","sys_msg":"success",'index':i_list,'data':d_list}
    return json_data


