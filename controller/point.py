from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
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

point = Blueprint('point', __name__)

user = User()
channel = Channel()
ltp = Limit_time_point()
ltp_product = Ltp_product()


# 取得個人點數餘額
@point.route('/api/v1/user_point/<channel_id>/<user_id>')
def user_point(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    
    point = ltp.user_point_info(channel_id, user_id)
    # 取得下個到期日
    n  = arrow.now()
    limit = n.shift(months=-13).format("YYYY-MM")
    # 計算將過期量
    point['limit'] = n.format("YYYY-MM")
    point['limit_last_point'] = 0
    # point['limit_last_point'] = ltp.get_month_last(limit,channel_id, user_id)
    json_data = {
                    'sys_code':"200",
                    "sys_msg":"success",
                    "point":point
                }
    return json_data



# 點數異動
@point.route('/api/v1/ch_point/<channel_id>/<user_id>', methods=['GET','POST'])
def ch_point(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    r = request.get_json()
    # 設定點數到期日
    limit = ''
    if 'limit' in r:
        limit = r['limit']
    else :
        if r['act'] == 'add':
            limit = arrow.now().shift(years=+1).format("YYYY-MM")
    # 寫入點數
    ltp.ch_point(channel_id,user_id,r['point'],r['note'],r['act'],limit)
    # 取回資料
    json_data = {
        'sys_code':'200',
        'sys_msg':'success',
        'data':ltp.user_point_info(channel_id, user_id)
    }
    return json_data

# 點數紀錄
@point.route('/api/v1/log_point/<channel_id>/<user_id>/<act>', methods=['GET', 'POST'])
def log_point(channel_id, user_id,act):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    
    
    datalist = ltp.user_point_log(channel_id,user_id,act)
    json_data = {
        'sys_code':'200',
        'sys_msg':'success',
        'data':datalist
    }
    return json_data

# 序號商品
# 設定商品
@point.route('/api/v1/set_product/<channel_id>', methods=['GET', 'POST'])
def set_product(channel_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    data = request.get_json()
    data['channel_id'] = channel_id
    ltp_product.set_product(data)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
# 取得商品清單
@point.route('/api/v1/list_product/<channel_id>', methods=['GET', 'POST'])
def list_product(channel_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    datalist =ltp_product.list_product(channel_id)
    json_data = {'sys_code':"200","sys_msg":"success","datalist":datalist}
    return json_data
# 建立訂單
@point.route('/api/v1/create_order/<channel_id>', methods=['GET', 'POST'])
def create_order(channel_id):
    return request.values

# 傳送單一訊息
@point.route('/api/v1/send_single_msg/<channel_id>/<user_id>', methods=['GET', 'POST'])
def send_single_msg(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    msg = Msg()
    data = request.get_json()
    msg.send_single_msg(channel_id,user_id,data['message'])
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data

# 傳送多筆訊息
@point.route('/api/v1/send_multicast_msg_by_tag', methods=['POST'])
def send_multicast_msg_by_tag():
    data = request.get_json()
    # 確認 channel_id
    if(channel.chk_once(data['channel_id']) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    tags = Tags()
    msg = Msg()
    users = tags.tag_users(data['channel_id'],data['tag'])
   
    if len(users) > 0:
        msg.send_multicast_msg(data['channel_id'],users,data['message'])
    json_data = {'sys_code':"200","sys_msg":"success","message":data['message'],"users":users}
    return json_data