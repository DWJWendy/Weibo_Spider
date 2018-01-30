#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
@author:毛毛虫_Wendy
@license:(C) Copyright 2017- 
@contact:dengwenjun@gmail.com
@file:Sipder.py
@time:10/26/17 5:36 PM
"""
import re, json,time
from program.Conn import MongoDB
from bs4 import BeautifulSoup
from program.Prelogin import login_weibo,getData
from program.logfile import logger

class Weibo_Spider(object):
    login_weibo("××××","××")
    def __init__(self):
        self.host = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100606&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&"
        self.ID = [1006062557129567,1006061902909102,1006061809745371,1006061689575103,1006061888640485,
                   1006061710173801,1006062183473425,1006061771925961,1006062968634427,1006062531246845,
                   1006061807956030,1006062156294570,1006065183764432,1006061698698394,1006062683843043,
                   1006061890174912,1006062798510462,]

        self.ID_page_num = self.get_page()
        self.ID_urls = self.get_urls()

    def get_urls(self):
        logger.info('生成所有爬取网页的URLs...')
        ID_urls = {}
        for id in range(len(self.ID)):
            urls = []
            for i in range(1, self.ID_page_num[id]+1):
                urls.append(self.host+"page="+str(i)+"&pagebar=0&id="+str(self.ID[id]))
                for j in range(0, 2):
                    urls.append(self.host+"page="+str(i)+"&pagebar="+str(j)+"&id="+str(self.ID[id])+"&pre_page="+str(i))
            ID_urls[id]=urls
        return ID_urls


    def get_page(self):
        logger.info('获取所有页码...')
        ID_page_num = {}
        for id in range(len(self.ID)):
            text = getData(url=self.host + "page=1&pagebar=1&id=" + str(self.ID[id]) + "&pre_page=1")
            content = json.loads(text.decode("ascii"))['data']
        # -*- 查询总页数 -*-
            reg = 'countPage=(\d+)"'
            try:
                page_num = int(re.findall(reg, content, re.S)[0])
            except:
                page_num = 0
            ID_page_num[id] = page_num
        return ID_page_num

    def get_content(self,text):
        mongo = MongoDB()
        reg = '<em>(\d+)</em>'
        logger.info('解析获取网页数据...')
        content = json.loads(text.decode("ascii"))['data']
        soup = BeautifulSoup("<html><head></head><body>" + content + "</body></html>", "lxml")
        tmp = soup.find_all("div", attrs={"class": "WB_detail"})
        tmp2 = soup.find_all("div", attrs={"class":"WB_handle"})
        if len(tmp) > 0 :
            for i in range(len(tmp)):
                item = {}
                item["nickname"] = tmp[i].find("div", attrs={"class": "WB_info"}).find("a").get_text()
                item["Post"] = tmp[i].find("div", attrs={"class": "WB_text W_f14"}).get_text().replace("\n", "").replace(" ","").replace( "\u200b", "")

                # -*- 爬取发布时间 -*-
                item["Pubtime"] = tmp[i].find("a", attrs={"class": "S_txt2"}).get("title")

                # -*- 爬取转发数 -*-
                if re.findall(reg,str(tmp2[i].find("span", attrs={"class": "line S_line1","node-type":"forward_btn_text"})), re.S):
                    item["Transfer_num"] = int(re.findall(reg,str(tmp2[i].find("span", attrs={"class": "line S_line1","node-type":"forward_btn_text"})), re.S)[0])
                else:
                    item["Transfer_num"] = 0

                # -*- 爬取评论数 -*-
                if re.findall(reg, str(tmp2[i].find("span", attrs={"class": "line S_line1", "node-type": "comment_btn_text"})), re.S):
                    item["Comment_num"] = int(re.findall(reg, str(tmp2[i].find("span", attrs={"class": "line S_line1", "node-type": "comment_btn_text"})), re.S)[0])
                else:
                    item["Comment_num"] = 0

                # -*- 爬取点赞数 -*-
                if re.findall(reg, str(tmp2[i].find("span", attrs={"node-type": "like_status"})), re.S):
                    item["Like_num"] = int(re.findall(reg, str(tmp2[i].find("span", attrs={"node-type": "like_status"})), re.S)[0])
                else:
                    item["Like_num"] = 0
                item["Scraltime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                if mongo.process_item(item)== "null":
                    break
                else:
                    continue



if __name__ == "__main__":
    a = Weibo_Spider()
    print(a.ID_page_num)
