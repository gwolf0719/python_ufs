#coding=utf-8
from flask import Flask, jsonify, request, render_template,session
import pymongo
import pandas as pd
import datetime
import time
import numpy as np

class Database:
    def __init__(self):
        # self.client = pymongo.MongoClient("mongodb+srv://james:wolf0719@cluster0-oiynz.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.client = MongoClient('127.0.0.1', 27017)
        self.client.admin.authenticate('james', 'wolf0719')
        
    def set_db(self):
        return self.client.ufs
    