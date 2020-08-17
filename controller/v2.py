from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import json
import hashlib

from data_model.channel import *
from data_model.user import *
# from data_model.limit_time_point import *

v2 = Blueprint('v2', __name__)

user = User()
channel = Channel()
# ltp = Limit_time_point()

@v2.route('/limit_time_point/user_log/<channel_id>/<user_id>')
def limit_time_point_user_log(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data

    # user_info = limit_time_point.chk_once(channel_id, user_id)
    json_data = {'sys_code':"200","sys_msg":"success"}

    return json_data

