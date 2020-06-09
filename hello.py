from flask import Flask, jsonify, request, render_template,session,redirect,url_for,flash,Blueprint
import os
import re
import json
import pymongo
import pandas as pd
import datetime
import time
import numpy as np
import data_model.order 

# from dateutil import parser

order = Order()
order.rechk_last_product("1654253073")
# client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
# dblist = client.list_database_names()
# print(dblist)
# # nowDay = datetime.now()

# # 取得日期區間加入會員
# users = client.ufs.users.find(
#     {
#         "created_datetime":{"$gte" : datetime.datetime(2020, 3, 1), "$lt": datetime.datetime(2020, 5, 30)},
#         "channel_id":'1653459101'
#     }
# )


# datalist = []
# for row in users:
#     del row["_id"]
#     datalist.append(row)

# df = pd.DataFrame(datalist)
# df = df.set_index('created_datetime', inplace = False)

# df2 = df.resample('D')["user_id"].count()

# jsdata = df2.to_json(orient='split')
# # print(list(df2.index))
# d_list =[]
# for d in df2.index:
#     d = str(d)
#     d = d.split(' ')
#     d_list.append(d[0])

# print(d_list)
