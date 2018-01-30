#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
@author:毛毛虫_Wendy
@license:(C) Copyright 2017- 
@contact:dengwenjun@gmail.com
@file:Conn.py
@time:10/26/17 5:37 PM
"""
import pymongo
from program.logfile import logger

class MongoDB(object):
    def __init__(self):
        # -*- 链接数据库 -*-
        clinet = pymongo.MongoClient("localhost", 27017)
        db = clinet["Weibo201801"]
        self.data = db["data"]

    def process_item(self, item):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, dict):
            if self.data.find_one({"nickname":item["nickname"],"Post":item["Post"],"Pubtime":item["Pubtime"]}):
                return "null"
            else:
                self.data.insert(item)
                logger.info("insert data into database...")
                return "ok"



