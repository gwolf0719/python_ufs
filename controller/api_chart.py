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

# 標籤趨勢
@api_chart.route('/api_chart/tag_daily/<channel_id>/<start>/<end>')
def tag_daily(channel_id, start, end):
    
    index = pd.date_range(start=start,end=end, freq='D')
     # 製做 index list
    index_list =[]
    for i in index :
        i = str(i)
        i = i.split(' ')
        index_list.append(i[0])
    # print(index)

    tag_logs = db.ufs.tag_log.find(
        {
            "time":{
                "$gte" : datetime.datetime(int(start.split("-")[0]), int(start.split("-")[1]), int(start.split("-")[2])),
                "$lt": datetime.datetime(int(end.split("-")[0]), int(end.split("-")[1]), int(end.split("-")[2]))
            },
            "channel_id":channel_id
        }
    )
    fulldatalist = []
    for row in tag_logs:
        del row["_id"]
        fulldatalist.append(row)
    # 將資料轉成 DataFrame
    df = pd.DataFrame(fulldatalist)
    
    # # 取得 tag 清單
    tags = db.ufs.tag_main.find({"channel_id":channel_id})
    datas_tags=[]
    tag_names = []
    for t in tags:
        datas = []
        tag_names.append(t["tag_desc"])
        count_list = []
        for i in index_list:
            if tag in df:
                mask1 = df['tag'] == t['tag']
                mask2 = df['time'].between(i+" 00:00:00",i+" 23:59:59")
                c = df[mask1 & mask2 ].count()
                count_list.append(int(c.values[0]))
            else:
                count_list.append(0)
        datas = {
            "name":t["tag_desc"],
            "type": 'line',
            "stack": '總量',
            "data":count_list
        }
        datas_tags.append(datas)
    return {"index":index_list,'datas':datas_tags,'tags':tag_names}

# 單一標籤統計
@api_chart.route('/api_chart/tag_daily_once/<tag>/<channel_id>/<start>/<end>')
def tag_daily_once(tag,channel_id, start, end):
    
    index = pd.date_range(start=start,end=end, freq='D')
     # 製做 index list （日期）
    index_list =[]
    for i in index :
        i = str(i)
        i = i.split(' ')
        index_list.append(i[0])
    # 取得所有需要的資料
    find = {
            "time":{
                "$gte" : datetime.datetime(int(start.split("-")[0]), int(start.split("-")[1]), int(start.split("-")[2])),
                "$lt": datetime.datetime(int(end.split("-")[0]), int(end.split("-")[1]), int(end.split("-")[2]))
            },
            "channel_id":channel_id,
            "tag":tag
        }
    tag_logs = db.ufs.tag_log.find(find)
    
    fulldatalist = []
    for row in tag_logs:
        del row["_id"]
        fulldatalist.append(row)
    # 將資料轉成 DataFrame
    df = pd.DataFrame(fulldatalist)
    
    datas = []
    count_list = []
    for i in index_list:
        if tag in df:
            mask1 = df['tag'] == tag
            mask2 = df['time'].between(i+" 00:00:00",i+" 23:59:59")
            c = df[mask1 & mask2 ].count()
            count_list.append(int(c.values[0]))
        else:
            count_list.append(0)
    datas = {
        "name":tag,
        "type": 'line',
        "data":count_list
    }
    return {"index":index_list,'datas':datas,'tag':tag}

    

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


