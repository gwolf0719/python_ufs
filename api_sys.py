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
    

    # 設定發送內容
    if msg_data["type"] == "text":
        send_message = TextSendMessage(text=msg_data["text"])
    elif msg_data["type"] == "image":
        send_message = ImageSendMessage(
            original_content_url=msg_data['original_content_url'],
            preview_image_url=msg_data['original_content_url']
        )
    elif msg_data['type'] == "imagemap":
        send_message = ImagemapSendMessage(
            base_url=msg_data['base_url'],
            alt_text=msg_data['alt_text'],
            base_size=BaseSize(height=1040, width=1040),
            actions=[
                URIImagemapAction(
                    link_uri=msg_data['link_uri'],
                    area=ImagemapArea(
                        x=0, y=0, width=1040, height=1040
                    )
                )
            ]
        )


    users = []
    user_ids = []
    line_bot_api = LineBotApi(channel_access_token)
    users = user.get_all_users(channel_id)
        
    
    for user_data in users:
        user_ids.append(user_data['user_id'])
        # 設定log
        user.set_user_log(user_data['user_id'],channel_id,"發送訊息"+msg_data['subject'])
        res = line_bot_api.push_message(user_data['user_id'], send_message)


    
    # for user in users:
    
    # line_bot_api.multicast(user_ids, text_send_message)
    json_data = {'sys_code':"200","sys_msg":"success"}

    return json_data

