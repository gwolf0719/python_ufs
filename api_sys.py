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
from data_model.chat import *
from data_model.order import *


api_sys = Blueprint('api_sys', __name__)


        

# 設定後台 session channel
@api_sys.route('/api_sys/set_channel/<channel_id>')
def set_channel(channel_id):
    session["channel_id"] = channel_id
    manager_id = session.get("manager_id")
    channel = Channel()
    channel_info = channel.get_channel_manger(channel_id,manager_id)
    session['level'] = channel_info['level'];
    json_data = {'sys_code':"200","sys_msg":"success",'channel_id':channel_id}
    return json_data




# 發送
# @api_sys.route('/api_sys/send_message/<channel_id>/<msg_id>/<user_id>')
# def send_message(channel_id,msg_id,user_id):
#     msg = Msg()
#     channel = Channel()
#     user = User()
#     # user_id = "Ufd5d3bb5d828bfcef65344c0bd5b5c07"
#     msg_data = msg.get_once(msg_id)
#     msg.send_message(channel_id,msg_id,user_id)

#     # # # 整理會員名單
#     # users = []
#     # user_ids = []
#     # users = user.get_all_users(channel_id)
#     # # line_bot_api = LineBotApi(channel_access_token)
#     # # # U7e053ed8fcca7e8bf4b82ac79accf8cc
#     # # # res = line_bot_api.push_message('U7e053ed8fcca7e8bf4b82ac79accf8cc', send_message)
#     # # # 發送訊息
#     # for user_data in users:
        
#     #     # 設定log
#     #     user.set_user_log(user_data['user_id'],channel_id,"發送訊息"+msg_data['subject'])
#     #     msg.send_message(channel_id,msg_id,user_data['user_id'])

#     json_data = {'sys_code':"200","sys_msg":"success"}

#     return json_data



# 取得聊天室清單
@api_sys.route('/api_sys/get_chat_room/<channel_id>')
def get_chat_room(channel_id):
    chat = Chat()
    room_list = chat.get_chat_room(channel_id)
    json_data = {'sys_code':"200","sys_msg":"success","room_list":room_list}
    return json_data
# 刪除聊天室
@api_sys.route('/api_sys/remove_chat_room/<channel_id>/<user_id>')
def remove_chat_room(channel_id, user_id):
    chat = Chat()
    chat.remove_chat_room(channel_id,user_id)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
@api_sys.route('/api_sys/open_chat_room/<channel_id>/<user_id>')
def open_chat_room(channel_id, user_id):
    chat = Chat()
    user = User()
    user_data = user.get_once(user_id,channel_id)
    room_data = {
                'channel_id':channel_id,
                'user_id':user_id,
                'name':user_data['name'],
                'read_status':0,
                'avator':user_data['avator']
            }
            # self.col_chat_room.insert_one(room_data)
    chat.open_chat_room(room_data)

    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
# 取得個人訊息內容列
@api_sys.route('/api_sys/get_chat_msg/<channel_id>/<user_id>')
def get_chat_msg(channel_id, user_id):
    chat = Chat()
    datalist = chat.get_user_chat(channel_id, user_id)
    json_data = {'sys_code':"200","sys_msg":"success","datalist":datalist}
    return json_data


# 後台回覆私訊
@api_sys.route('/api_sys/return_chat_msg/<channel_id>/<user_id>')
def return_chat_msg(channel_id, user_id):
    chat = Chat()
    msg = Msg()
    channel = Channel()
    text_info = request.values['text_info']
    
    text_info = text_info.replace('<br>','\n')
    channel_access_token = channel.get_channel(channel_id)['channel_access_token']
    # 取得最後一筆資料 ，優先用回覆
    last_chat = chat.get_user_chat(channel_id, user_id)[-1]
    replyToken = last_chat['replyToken']
    send_message = TextSendMessage(text=text_info)
    line_bot_api = LineBotApi(channel_access_token)
    try:
        
        line_bot_api.push_message(user_id, send_message)
        
    except BaseException:
            line_bot_api.reply_message(replyToken, send_message)
    
    
        # 寫入記錄
    chat_data = {
                    "user_id":user_id,
                    "channel_id":channel_id,
                    "text":text_info,
                    "replyToken":"",
                    "read_status":1,
                    "name":last_chat['name'],
                    "avator":last_chat['avator'],
                    "originator":"admin"
                }
    datetime = chat.add_chat(chat_data)
    # 設定已讀
    chat.set_read(channel_id,user_id)
    json_data = {'sys_code':"200","sys_msg":"success",'datetime':datetime}
    return json_data

##############################################
## 自動回覆 
##############################################
@api_sys.route('/api_sys/set_auto_reply/', methods=["GET","POST"])
def set_auto_reply():
    jsondata = request.get_json()
    channel_id = jsondata['channel_id']
    chat = Chat()
    if chat.chk_auto_reply(channel_id) == True:
        chat.update_auto_reply(channel_id,jsondata)
    else:
        chat.add_auto_reply(jsondata)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
@api_sys.route('/api_sys/get_auto_reply/<channel_id>')
def get_auto_reply(channel_id):
    channel = Channel()
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    chat = Chat()
    if chat.chk_auto_reply(channel_id) == False:
        json_data = {'sys_code':"404","sys_msg":"auto_reply not found"}
        return json_data
    else:
        auto_reply = chat.get_auto_reply(channel_id)
        json_data = {'sys_code':"200","sys_msg":"Success","auto_reply":auto_reply}
        return json_data


##############################################
## 訂單 
##############################################
# channel_id,order_id,exchange_link,exchange_code
@api_sys.route('/api_sys/order_set_exchange')
def order_exchange():
    channel = Channel()
    order = Order()
    channel_id = request.values['channel_id']
    order_id = request.values['order_id']
    exchange_link = request.values['exchange_link']
    exchange_code = request.values['exchange_code']
    
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    if order.chk_once(channel_id,order_id) == False:
        json_data = {'sys_code':"404","sys_msg":"order not found"}
        return json_data
    order_info = order.get_once(channel_id,order_id)
    if order_info['status'] == 'applying':
        json_data = {'sys_code':"200","sys_msg":"Success"}
        order.pass_one(channel_id,order_id,{"exchange_link":exchange_link,"exchange_code":exchange_code,"status":"pass"})
    else:
        json_data = {'sys_code':"500","sys_msg":"status fail"}
    json_data['info'] = order_info;
    return json_data

# 取消訂單
@api_sys.route('/api_sys/order_cancel', methods=["GET", "POST"])
def order_cancel():
    channel = Channel()
    order = Order()
    channel_id = request.values['channel_id']
    order_id = request.values['order_id']
    
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    if order.chk_once(channel_id,order_id) == False:
        json_data = {'sys_code':"404","sys_msg":"order not found"}
        return json_data

    order_info = order.get_once(channel_id,order_id)
        
    order.cancel_order(channel_id,order_id)
    # 重新計算庫存量
    order.rechk_last_product(channel_id)
    json_data = {'sys_code':"200","sys_msg":"Success"}
    
    json_data['info'] = order_info;
    return json_data



#============================================================================
    #
    # 
    # 標籤
    #
    # 
    # =================================================================
# =================================================================

@api_sys.route('/api_sys/set_tag_main', methods=['POST'])
def set_tag_main():
    jsondata = request.get_json()
    jsondata['channel_id']  = str(jsondata['channel_id'])
    jsondata['limit_qty']  = int(jsondata['limit_qty'])
    
    # 新增標籤增加配點功能 ＠2020-06-08
    if jsondata['user_add_point_value'] != "0" :
        jsondata['act'] = []
        jsondata['act'].append({
            'act_key':"add_user_point",
            "act_value":jsondata['user_add_point_value']
        })
    del jsondata['user_add_point_value']
    tags = Tags()
    if tags.chk_once(jsondata['channel_id'],jsondata['tag']) == True:
        return  {'sys_code':"500","sys_msg":"重複設定"}
    else:
        tags.set_tag_main(jsondata)
        return  {'sys_code':"200","sys_msg":"Success"}

