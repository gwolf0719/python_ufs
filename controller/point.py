from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import json
import hashlib
import arrow

from data_model.channel import *
from data_model.user import *
from data_model.limit_time_point import *

point = Blueprint('point', __name__)

user = User()
channel = Channel()
ltp = Limit_time_point()


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
    limit = n.shift(months=+1).format("YYYY-MM")
    # 計算將過期量
    point['limit'] = limit
    point['limit_last_point'] = ltp.get_month_last(limit,channel_id, user_id)
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
    r = request.values
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
    