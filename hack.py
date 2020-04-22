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


hack = Blueprint('hack', __name__)


# 重新計算每個會員的總累計點數
@hack.route('/hack/reset_user_lifetime_record')
def reset_user_lifetime_record():
    user = User()
    client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
    col_user = client.ufs.users
    col_point_logs = client.ufs.point_logs
    # 取得全部沒有計算總點數的
    datalist = []
    find = {'lifetime_record_point':{ '$exists': False } }
    # find = {}
    for d in col_user.find(find):
        del d["_id"]
        d['lifetime_record_point'] = user.lifetime_record(d['user_id'],d['channel_id'])
        find = {
            "user_id":d['user_id'],
            "channel_id":d['channel_id'],
        }
        # data["lifetime_record_point"] =d['lifetime_record_point']
        col_user.update_one(find,{"$set":{"lifetime_record_point":d['lifetime_record_point']}})

        datalist.append(d)
    json_data = {'sys_code':"200","sys_msg":"success","datalist":datalist}
    return json_data