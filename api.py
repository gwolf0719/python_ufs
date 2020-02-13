from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import json

# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *



api = Blueprint('api', __name__)
user = User()
channel = Channel()

# 第三方使用 API
# 會員
# =================================================================
# 取得會員資料
@api.route("/api/v0/get_user_info/<channel_id>/<user_id>", methods=["POST", "GET"])
def v0_get_user_info(channel_id,user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    
    user_info = user.get_once(user_id,channel_id)
    del user_info['tags'] # 不需要歷史紀錄
    json_data = {'sys_code':"200","sys_msg":"success","data":user_info}

    return json_data



# =================================================================    
# 設定會員資料 
@api.route("/api/v0/set_user_info/<channel_id>/<user_id>", methods=["POST", "GET"])
def v0_set_user_info(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    
    # 取得輸入資料
    jsondata = request.get_json()
    update_data = {}
    if ("name" in jsondata):
        update_data['name'] = jsondata["name"]
    if ("avator" in jsondata):
        update_data['avator'] = jsondata["avator"]
    # 輸入更新
    user.update_user_main(user_id,channel_id,update_data)
    # 取得會員資料
    user_info = user.get_once(user_id,channel_id)
    del user_info['tags'] # 不需要歷史紀錄
    json_data = {'sys_code':"200","sys_msg":"success","data":user_info}

    return json_data

# 設定會員標籤
@api.route('/api/v0/set_user_tag/<channel_id>/<user_id>/<tag>')
def v0_set_user_tag(channel_id,user_id,tag):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    # 設定 tag
    user.set_user_tag(user_id,channel_id,tag)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
# 取回會員標籤清單
@api.route('/api/v0/get_user_tags/<channel_id>/<user_id>/')
def get_user_tags(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    tags = user.get_user_tags(user_id,channel_id )
    json_data = {'sys_code':"200","sys_msg":"success","tags":tags}

    return json_data