from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import json
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

api_sys = Blueprint('api_sys', __name__)

@api_sys.route('/api_sys/set_channel/<channel_id>')
def set_channel(channel_id):
    session["channel_id"] = channel_id
    json_data = {'sys_code':"200","sys_msg":"success",'channel_id':channel_id}

    return json_data

# 設定發送名單排程隊列
@api_sys.route('/api_sys/send_message/<channel_id>/<msg_id>')
def send_message(channel_id,msg_id):
    msg = Msg()
    channel = Channel()
    user = User()

    channel_info = channel.get_channel(channel_id)
    channel_access_token = channel_info['channel_access_token']
    msg_data = msg.get_once(msg_id)
    if msg_data["type"] == "text":
        text_send_message = TextSendMessage(text=msg_data["text"])
    else:
        text_send_message = TextSendMessage(text="hello")
    users = []
    user_ids = []
    if msg_data["need_tags"] == "":
        users = user.get_all_users(channel_id)
    
    for user_data in users:
        user_ids.append(user_data['user_id'])
        # 設定log
        user.set_user_log(user_data['user_id'],channel_id,"發送訊息: "+msg_data['text'])

    line_bot_api = LineBotApi(channel_access_token)
    # for user in users:
    # line_bot_api.push_message("Ufd5d3bb5d828bfcef65344c0bd5b5c07", text_send_message)
    line_bot_api.multicast(user_ids, text_send_message)
    json_data = {'sys_code':"200","sys_msg":"success"}

    return json_data

