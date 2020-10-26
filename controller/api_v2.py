from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import math
import os
import json
import hashlib
import arrow
# line bot 相關元件
from linebot import LineBotApi
from linebot.models import *
from linebot.exceptions import LineBotApiError

from data_model.channel import *
from data_model.user import *
from data_model.limit_time_point import *
from data_model.ltp_product import *
from data_model.msg import *

api_v2 = Blueprint('api_v2', __name__)

user = User()
channel = Channel()
ltp = Limit_time_point()
ltp_product = Ltp_product()


# 取得會員清單 API 
@api_v2.route('/api/v2/channel_users/<channel_id>', methods=["POST"])
def users(channel_id):
    user = User()
    get_post_data= request.get_json()
    if "find" in get_post_data:
        find = get_post_data['find']
    else:
        find = {}
    if "limit" in get_post_data:
        limit = get_post_data['limit']
    else:
        limit = 100
    
    if "now_page" in get_post_data:
        now_page = get_post_data['now_page']
    else:
        now_page = 1;
    skip = (int(now_page)-1)*limit

    
    datalist = user.find_user_list(channel_id,find,skip,limit)
    date_count = user.find_user_list_count(channel_id,find)
    if date_count % limit == 0:
        page_items = date_count / limit
    else:
        page_items = math.floor(date_count / limit) + 1
    
    # # draw = request.values['draw']
    # draw = 1
    
    # order_column = request.values.get('search[value]')
    # # order_column = request.values['order']
    # # order_dir = request.values['order'][0]['dir']
    # # print(order_column)
    # # print(order_dir)
    # # search = request.values.get('search[value]')
    # # start = request.values['start'] 
    # # length = request.values['length']
    # datalist = user.find_list(channel_id,1,10,'')

    json_data = {
        "now_page":now_page,
        "skip":skip,
        "limit":limit,
        "datalist":datalist,
        "date_count":date_count,
        "page_items":int(page_items)
    }
    return json_data