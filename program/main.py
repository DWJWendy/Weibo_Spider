#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
@author:毛毛虫_Wendy
@license:(C) Copyright 2017- 
@contact:dengwenjun@gmail.com
@file:main.py
@time:11/9/17 11:33 AM
"""
import sched, time
from program.Spider import Weibo_Spider
from program.Prelogin import getData
from program.logfile import logger


# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)

def domain():
    weibospider = Weibo_Spider()
    ID_urls = weibospider.ID_urls
    for i in range(len(ID_urls)):
        for j in range(len(ID_urls[i])):
            logger.info('正在爬取第'+str(i)+"个账号 第"+str(j+1)+"条网页")
            weibospider.get_content(text=getData(ID_urls[i][j]))

def perform(inc):
    schedule.enter(inc, 0, perform, (inc,))
    domain()  # 需要周期执行的函数

def mymain():
    schedule.enter(0, 0, perform, (86400,))


if __name__ == "__main__":
    mymain()
    schedule.run()  # 开始运行，直到计划时间队