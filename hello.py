from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import re
import json
import pymongo
import pandas as pd
import datetime 
import time
import numpy as np

# line bot 相關元件
from linebot import LineBotApi
from linebot.models import *
from linebot.exceptions import LineBotApiError
# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *
from data_model.msg import *
from data_model.chat import *
from data_model.order import *



client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
col_user = client.ufs.users
col_point_logs = client.ufs.point_logs
col_webhook_log = client.ufs.webhook_log
# 1585699200
find = {"channel_id":"1653459101","act":"add","update_datetime":{'$lte':datetime.datetime.utcfromtimestamp(1585699200)}}
logs_data = col_point_logs.find(find)
datalist = []
point = 0
for row in logs_data:
    print(row)
    point = point+row['point']

print("point=====")
print(point)
# find = {
#     "events.type":"unfollow"
# }
# logs_data = col_webhook_log.find(find)
# datalist = []
# for row in logs_data:
#     del row["_id"]
#     print(row)
#     print(row["events"]['source']['userId'])
#     timeArray = time.localtime(row["events"]['timestamp']/1000)
#     print(timeArray)
#     otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
#     print(otherStyleTime)
#     find = {
#             "user_id":row["events"]['source']['userId'],
#             "channel_id":row['channel_id'],
#         }
#     data = {}
#     data["status"] ='unfollow'
#     data["unfollow_datetime"] =otherStyleTime
#     col_user.update_one(find,{"$set":data})