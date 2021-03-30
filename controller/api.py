from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import json
import hashlib
import requests
import random


# Model
from data_model.manager import *
from data_model.channel import *
from data_model.webhook import *
from data_model.user import *
from data_model.tags import *
from data_model.msg import *
from data_model.re_url import *
from data_model.product import *
from data_model.order import *
from data_model.chat import *


api = Blueprint('api', __name__)
user = User()
channel = Channel()

 #============================================================================
    #
    # 
    # 會員
    #
    # 
    # =================================================================
# =================================================================


# 重設手機驗證
@api.route('/api/v1/reset_mobile_chk/<channel_id>/<user_id>')
def reset_mobile_chk(channel_id, user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    data = {
        "mobile":"",
        "mobile_chk":False,
        "mobile_code":""
    }
    user.update_user_main(user_id,channel_id,data)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data

# 發送簡訊驗證
@api.route('/api/v0/send_mobile_chk/<channel_id>/<user_id>/<mobile>')
def send_mobile_chk(channel_id, user_id,mobile):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data

    user_info = user.get_once(user_id,channel_id)
    if 'mobile_chk' in user_info:
        if user_info['mobile_chk'] == True:
            json_data = {'sys_code':"500","sys_msg":"重複驗證"}
            return json_data

    # 送出簡訊驗證
    user.set_mobile_chk_code(channel_id,user_id,mobile)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data


# 驗證簡訊
@api.route('/api/v0/chk_mobile_code/<channel_id>/<user_id>/<mobile_code>')
def chk_mobile_code(channel_id, user_id,mobile_code):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data

    user_info = user.get_once(user_id,channel_id)
    if 'mobile_chk' in user_info:
        if user_info['mobile_chk'] == True:
            json_data = {'sys_code':"500","sys_msg":"重複驗證"}
            return json_data
    else:
        json_data = {'sys_code':"500","sys_msg":"尚未申請驗證碼"}
        return json_data

    # 送出簡訊驗證
    if user.chk_mobile_code(channel_id,user_id,mobile_code) == True:
        json_data = {'sys_code':"200","sys_msg":"success"}
    else:
        json_data = {'sys_code':"500","sys_msg":"驗證碼不正確"}
    return json_data


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
    if "tags" in user_info:
        del user_info['tags'] # 不需要歷史紀錄
    json_data = {'sys_code':"200","sys_msg":"success","data":user_info}

    return json_data
@api.route("/api/v1/chk_line_user_profile/<channel_id>/<user_id>", methods=["POST", "GET"])
def v1_chk_line_user_profile(channel_id, user_id):
    channel = Channel()
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # chk_line_user_profile(self,channel_id,user_id,channel_access_token)
    channel_info = channel.get_channel(channel_id)
    channel_access_token = channel_info['channel_access_token']
    if(user.chk_line_user_profile(channel_id,user_id,channel_access_token) == True):
        json_data = {'sys_code':"200","sys_msg":"line user success"}
    else:
        json_data = {'sys_code':"404","sys_msg":"line user not found"}
    return json_data

# 設定會員資料，如果沒有資料就新增
@api.route("/api/v1/set_user/<channel_id>/<user_id>", methods=["POST", "GET"])
def v1_set_user(channel_id, user_id):
    channel = Channel()
    json_data = {}
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == True):
        data = {}
        user.update_user_main(user_id,channel_id,data)
    else:
        channel_info = channel.get_channel(channel_id)
        channel_access_token = channel_info['channel_access_token']
        
        
        if user.add_once(user_id,0,channel_id,channel_access_token) == True:
            # 取得會員資料

            user_info = user.get_once(user_id,channel_id)
            print(user_info)
            json_data = {'sys_code':"200","sys_msg":"success","data":user_info}
        else:
            print(channel_access_token)
            print(channel_id)
            print(user_id)
            json_data = {'sys_code':"500","sys_msg":"id error"}
   
    return json_data
    

@api.route("/api/v0/add_user/<channel_id>/<user_id>", methods=["POST", "GET"])
def v0_add_user(channel_id, user_id):
    channel = Channel()
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == True):
        json_data = {'sys_code':"500","sys_msg":"會員重覆"}
        return json_data
    
    
    channel_info = channel.get_channel(channel_id)
    channel_access_token = channel_info['channel_access_token']
    block = 0;
    if "block" in request.values:
        block = request.values['block']
    
    if user.add_once(user_id,block,channel_id,channel_access_token) == True:
        # 取得會員資料
        user_info = user.get_once(user_id,channel_id)
        json_data = {'sys_code':"200","sys_msg":"success","data":user_info}
    else:
        json_data = {'sys_code':"500","sys_msg":"id error"}

    return json_data


# 刪除會員
@api.route('/api/v0/remove_user/<channel_id>/<user_id>')
def v0_remove_user(channel_id, user_id):
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    user.remove(channel_id, user_id)
    json_data = {'sys_code':"200","sys_msg":"Success"}
    return json_data
    

# # 設定會員標籤
@api.route('/api/v0/set_user_tag/<channel_id>/<user_id>/<tag>')
def v0_set_user_tag(channel_id,user_id,tag):
    # user = User()
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if user_id != "Guest":
        if(user.chk_once(user_id,channel_id) == False):
            json_data = {'sys_code':"404","sys_msg":"user not found"}
            return json_data
    # 設定 tag
    # tags = Tags()
    user.set_user_tag(user_id,channel_id,tag)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data
@api.route('/api/v1/set_user_tag', methods=['POST'])
def v1_set_user_tag():
    data = request.get_json()
    channel_id = data['channel_id']
    user_id = data['user_id']
    tag = data['tag']
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if user_id != "Guest":
        if(user.chk_once(user_id,channel_id) == False):
            json_data = {'sys_code':"404","sys_msg":"user not found"}
            return json_data
    # 設定 tag
    # tags = Tags()
    user.set_user_tag(user_id,channel_id,tag)
    json_data = {'sys_code':"200","sys_msg":"success"}
    return json_data

# # 取回會員標籤清單
@api.route('/api/v0/get_user_tags/<channel_id>/<user_id>/')
def get_user_tags(channel_id, user_id):
    tags = Tags()
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    tag_list = tags.user_tags(channel_id,user_id )
    json_data = {'sys_code':"200","sys_msg":"success","tags":tag_list}

    return json_data

# 取得單一標籤被使用的會員
@api.route('/api/v0/get_tag_users/<channel_id>/<tag>')
def get_tag_users(channel_id, tag):
    tags = Tags()
    users = tags.tag_users(channel_id,tag,'true')
    return {'sys_code':"200","sys_msg":"success","users":users}
# 取得單一標籤追蹤中的會員數量
@api.route('/api/v0/get_tag_qty/<channel_id>/<tag>')
def get_tag_qty(channel_id, tag):
    tags = Tags()
    qty = len(tags.tag_users(channel_id,tag,'true'))
    return {'sys_code':"200","sys_msg":"success","qty":qty}

# 取得所有的標籤
@api.route('/api/v0/get_tag_list/<channel_id>')
def get_tag_list(channel_id):
    tags = Tags()
    tags = tags.all_tags_users(channel_id)
    return {'sys_code':"200","sys_msg":"success","tags":tags}

# 取得須要被統計的標籤使用次數
# track_types read_ranking=>指定閱讀,share_ranking=>分享連結
@api.route('/api/v0/get_tag_count/<channel_id>/<user_id>/<track_types>')
def get_tag_count(channel_id, user_id,track_types):
    tags = Tags()
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    
    # 取得要被追縱的 tag
    t_tags = tags.track_types(channel_id,track_types)
    # print(t_tags)
    c = tags.track_types_count(channel_id,user_id,t_tags)
    # print(c)
    json_data = {'sys_code':"200","sys_msg":"Success","count":c}
    return json_data

# 取得須要被分享的資料
@api.route('/api/v0/get_share_info/<channel_id>/<user_id>/<link_id>')
def get_share_info(channel_id, user_id, link_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data

    # 取得內容
    re_url = Re_url()
    re_url_data = re_url.get_once(link_id)
    
    if 'type' in re_url_data:
        if re_url_data['type'] == 'share':
        # 設定對應標籤
            tag = re_url_data['tags']
            user.set_user_tag(user_id,channel_id,re_url_data['tags'])
            
        json_data = {'sys_code':"200","sys_msg":"Success","desc":re_url_data["desc"]}
        # json_data = {'sys_code':"200","sys_msg":"Success","desc":"#地球一小時EarthHour 3/28(六)晚間8:30~9:30\n 瓜寶邀請你關燈一小時⚡️\n 一起關一波作伙愛地球🌎\n \n 💝快閃小活動：關燈可以幹嘛？\n 快來發揮創意留言抽小禮物👉\n"}
        return json_data
    else:
        json_data = {'sys_code':"404","sys_msg":"查無資料"}
        return json_data

# 取得轉址資料
@api.route('/api/v0/get_re_url_info/<channel_id>/<user_id>/<link_id>')
def get_re_url_info(channel_id, user_id, link_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data

    # 取得內容
    re_url = Re_url()
    re_url_data = re_url.get_once(link_id)
    print(re_url_data)
    
    # 設定對應標籤
    if 'tags' in re_url_data:  
        tag = re_url_data['tags']
        user.set_user_tag(user_id,channel_id,re_url_data['tags'])
        json_data = {'sys_code':"200","sys_msg":"Success","target_url":re_url_data["target_url"]}
        return json_data
    else:
        json_data = {'sys_code':"404","sys_msg":"notfound"}
        return json_data
    



#============================================================================
    #
    # 
    # 點數
    #
    # 
    # =================================================================
# =================================================================
# # 增加點數
@api.route('/api/v0/add_user_point/<channel_id>/<user_id>', methods=["POST", "GET"])
def add_user_point(channel_id, user_id):
    jsondata = request.get_json()
    point = jsondata["point"]
    point_note = jsondata["point_note"]

    new_point = user.add_point(user_id,channel_id,point,point_note)
    json_data = {'sys_code':"200","sys_msg":"success",'new_point':new_point}

    return json_data


# 扣儲點數
@api.route('/api/v0/deduct_user_point/<channel_id>/<user_id>', methods=["POST", "GET"])
def deduct_user_point(channel_id, user_id):
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    jsondata = request.get_json()
    point = jsondata["point"]
    point_note = jsondata["point_note"]

    new_point = user.deduct_point(user_id,channel_id,point,point_note)
    json_data = {'sys_code':"200","sys_msg":"success",'new_point':new_point}

    return json_data

# # 點數查詢
@api.route('/api/v0/get_user_points/<channel_id>/<user_id>', methods=['GET'])
def get_user_points(channel_id, user_id):
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    user_data = user.get_once(user_id,channel_id)
    
    if "point" in user_data:
        point = user_data["point"]
        lifetime_record=user.lifetime_record(user_id,channel_id)
    else:
        point = 0
        lifetime_record = 0

    json_data = {
        "sys_code": "200",
        "sys_msg": "Success",
        "canuse_point": point,
        "used_point": lifetime_record-point,
        "lifetime_record":lifetime_record
    }
    return json_data
# 查詢點數記錄
@api.route('/api/v0/get_user_points_log/<channel_id>/<user_id>', methods=['GET'])
def get_user_points_log(channel_id, user_id):
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    user_data = user.get_once(user_id,channel_id)
    if "point" in user_data:
        point = user_data["point"]
        lifetime_record=user.lifetime_record(user_id,channel_id)
        point_logs = user.get_point_logs(user_id,channel_id)
    else:
        point = 0
        lifetime_record=0
        point_logs = []

    json_data = {
        "sys_code": "200",
        "sys_msg": "Success",
        "canuse_point": point,
        "used_point": lifetime_record-point,
        "lifetime_record":lifetime_record,
        "point_logs":point_logs
    }
    return json_data


#============================================================================
    #
    # 
    # 標籤
    #
    # 
    # =================================================================
# =================================================================

@api.route('/api/v0/set_tag_main', methods=['POST'])
def set_tag_main():
    jsondata = request.get_json()
    tags = Tags()
    if tags.chk_once(jsondata['channel_id'],jsondata['tag']) == True:
        return  {'sys_code':"500","sys_msg":"重複設定"}
    else:
        tags.set_tag_main(jsondata)
        return {'sys_code':"200","sys_msg":"Success"}





#============================================================================
    #
    # 
    # 商品兌換
    #
    # 
    # =================================================================
# =================================================================

# 商品清單
@api.route("/api/v0/products/<channel_id>/")
def products(channel_id):
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    product = Product()
    datalist = []
    for cate in product.product_categories_list(channel_id):
        cate["products"] = product.get_list(channel_id,cate['category_id'])
        datalist.append(cate)

    json_data = {
        "sys_code":"200",
        "sys_msg": "Success",
        "datalist":datalist
    }
    return json_data
# # 預購
# 2020-06-05 增加如果type= qr_ticket 就直接派發
@api.route("/api/v0/product_preorder/<channel_id>/<product_id>/<user_id>/<qty>")
def product_preorder(channel_id, product_id, user_id,qty):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    # 確認商品存在
    product = Product()
    if product.chk_once(channel_id,product_id) == False :
        json_data = {'sys_code':"404","sys_msg":"product not found"}
        return json_data
    p_data = product.get_once(channel_id,product_id)

    # 確認商品存量
    if int(product.chk_last(channel_id,product_id)) <= 0:
        json_data = {'sys_code':"500","sys_msg":"商品數量不足"}
        return json_data
    # 確認限購額度
    if 'single_limit' in p_data:
        if p_data['single_limit'] != '':
            single_limit = int(p_data['single_limit'])
            if single_limit > 0:
                order = Order()
                user_product_orders = order.user_product_orders(channel_id, user_id,product_id)
                if len(user_product_orders) >= single_limit:
                    json_data = {'sys_code':"500","sys_msg":"超過可以購買的量，請購買其它商品"}
                    return json_data

    # 確認需要點數
    need = int(p_data['need_points']) * int(qty)
    u_data = user.get_once(user_id,channel_id)
    used = u_data['point']
    if need > used:
        json_data = {'sys_code':"500","sys_msg":"點數不足"}
        return json_data
    # 預購
    order = Order()
    order_id = order.applying_preorder(channel_id,product_id,user_id,qty)
    # 重新計算庫存量
    order.rechk_last_product(channel_id)

    # 如果type= qr_ticket 就直接派發
    if p_data['type'] == 'qr_ticket':
        # 先將資料編碼，再更新 MD5 雜湊值
        
        exchange_link = '/chk_qr_ticket/'+channel_id+'/'+order_id+"/"
        exchange_code = hashlib.md5().hexdigest()[-4:]
        order.pass_one(channel_id,order_id,{"exchange_link":exchange_link,"exchange_code":exchange_code,"status":"pass"})


    json_data = {
        "sys_code":"200",
        "sys_msg": "Success"
    }
    return json_data

# # 兌換記錄
@api.route('/api/v0/get_user_preorder/<channel_id>/<user_id>')
def get_user_preorder(channel_id,user_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    order = Order()
    datalist = order.get_user_preorder(channel_id, user_id)
    json_data = {
        "sys_code":"200",
        "sys_msg": "Success",
        "datalist":datalist
    }
    return json_data

# 取得單一訂單
@api.route('/api/v0/get_order_once/<channel_id>/<order_id>')
def get_order_once(channel_id,order_id):
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    
    order = Order()
    data = order.get_once(channel_id, order_id)
    json_data = {
        "sys_code":"200",
        "sys_msg": "Success",
        "data":data
    }
    return json_data
# # 領取
@api.route('/api/v0/order_2_got/<channel_id>/<user_id>/<order_id>')
def order_2_got(channel_id,user_id,order_id):
    order = Order()
    # 確認 channel_id
    if(channel.chk_once(channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"channel not found"}
        return json_data
    # 確認 user_id
    if(user.chk_once(user_id,channel_id) == False):
        json_data = {'sys_code':"404","sys_msg":"user not found"}
        return json_data
    
    if order.chk_once(channel_id,order_id) == False:
        json_data = {'sys_code':"404","sys_msg":"order not found"}
        return json_data
    
    order_info = order.get_once(channel_id,order_id)
    if order_info['status'] == 'pass':
        order.order_2_got(channel_id,order_id)
        json_data = {'sys_code':"200","sys_msg":"Success"}
        return json_data
    else :
        json_data = {'sys_code':"500","sys_msg":"status fail"}
        json_data['info'] = order_info
        return json_data

    
    