from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import re
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

# 設定腳本
# 2020-03-09 改成 script 和 msg 共用設定和資廖庫
@api_sys.route('/api_sys/set_msg/', methods=["POST"])
def set_msg():
    # 取得輸入資料
    jsondata = request.get_json()
    # print(jsondata)
    # msg = Msg()
    # msg.add_once(jsondata)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
        


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
    

    # 設定發送內容
    # 純文字訊息
    if msg_data["msg_type"] == "text":
        send_message = TextSendMessage(text=msg_data["text"])
    # 圖片
    elif msg_data["msg_type"] == "image":
        send_message = ImageSendMessage(
            original_content_url=msg_data['original_content_url'],
            preview_image_url=msg_data['original_content_url']
        )
    # 圖片帶連結
    elif msg_data['msg_type'] == "imagemap":
        
        action = []
        action.append(URIImagemapAction(
                        link_uri="https://www.google.com.tw",
                        area=ImagemapArea(
                            x=0, y=0, width=520, height=1040
                        )
                ))
        action.append(MessageImagemapAction(
                                text="heell",
                                area=ImagemapArea(
                                    x=520, y=0, width=520, height=1040
                                )
                            ))
        send_message = ImagemapSendMessage(
            base_url=msg_data['base_url'],
            alt_text=msg_data['alt_text'],
            base_size=BaseSize(height=1040, width=1040),
            actions=action
        )

    # 整理會員名單
    users = []
    user_ids = []
    users = user.get_all_users(channel_id)
    line_bot_api = LineBotApi(channel_access_token)
    # U7e053ed8fcca7e8bf4b82ac79accf8cc
    res = line_bot_api.push_message('U7e053ed8fcca7e8bf4b82ac79accf8cc', send_message)
    # 發送訊息
    # for user_data in users:
    #     user_ids.append(user_data['user_id'])
    #     # 設定log
    #     user.set_user_log(user_data['user_id'],channel_id,"發送訊息"+msg_data['subject'])
    #     res = line_bot_api.push_message(user_data['user_id'], send_message)

    json_data = {'sys_code':"200","sys_msg":"success"}

    return json_data

