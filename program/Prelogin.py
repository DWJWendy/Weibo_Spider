#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
@author:毛毛虫_Wendy
@license:(C) Copyright 2017- 
@contact:dengwenjun@gmail.com
@file:Prelogin.py
@time:10/26/17 5:35 PM
"""
import re , urllib.parse , urllib.request , http.cookiejar , base64 , binascii , rsa , time, pprint, requests,json
from bs4 import BeautifulSoup
from program.Conn import MongoDB

# -*- 以下4行代码说简单点就是让你接下来的所有get和post请求都带上已经获取的cookie，因为稍大些的网站的登陆验证全靠cookie -*-
cj = http.cookiejar.LWPCookieJar()
cookie_support = urllib.request.HTTPCookieProcessor(cj)
opener = urllib.request.build_opener(cookie_support , urllib.request.HTTPHandler)
urllib.request.install_opener(opener)


def getData(url):
    """
    # 封装一个用于get的函数，新浪微博这边get出来的内容编码都是-8，所以把utf-8写死在里边了，真实项目中建议根据内容实际编码来决定
    :param url: 输入需要访问的url地址，返回text结果
    :return:
    """

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    text = response.read()
    time.sleep(3)
    return text

def postData(url , data) :
    """
    # 封装一个用于post的函数，验证密码和用户名都是post的，所以这个postData在本demo中专门用于验证用户名和密码
    :param url:
    :param data:
    :return:
    """
    # headers需要我们自己来模拟
    headers = {'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}
    # 这里的urlencode用于把一个请求对象用'&'来接来字符串化，接着就是编码成utf-8
    data = urllib.parse.urlencode(data).encode('utf-8')
    request = urllib.request.Request(url , data , headers)
    response = urllib.request.urlopen(request)
    text = response.read().decode('gbk')
    return text

def login_weibo(nick , pwd) :
    #==========================获取servertime , pcid , pubkey , rsakv===========================
    # 预登陆请求，获取到若干参数
    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.15)&_=1400822309846' % nick
    preLogin = getData(prelogin_url)
    # 下面获取的四个值都是接下来要使用的
    servertime = re.findall('"servertime":(.*?),' , preLogin.decode('utf-8'))[0]
    pubkey = re.findall('"pubkey":"(.*?)",' , preLogin.decode('utf-8'))[0]
    rsakv = re.findall('"rsakv":"(.*?)",' ,preLogin.decode('utf-8'))[0]
    nonce = re.findall('"nonce":"(.*?)",' , preLogin.decode('utf-8'))[0]

    #===============对用户名和密码加密================
    # 好，你已经来到登陆新浪微博最难的一部分了，如果这部分没有大神出来指点一下，那就真是太难了，我也不想多说什么，反正就是各种加密，最后形成了加密后的su和sp
    su = base64.b64encode(bytes(urllib.request.quote(nick) , encoding = 'utf-8'))
    rsaPublickey = int(pubkey , 16)
    key = rsa.PublicKey(rsaPublickey , 65537)
    #稍微说一下的是在我网上搜到的文章中，有些文章里并没有对拼接起来的字符串进行bytes，这是python3的新方法好像是。rsa.encrypt需要一个字节参数，这一点和之前不一样。其实上面的base64.b64encode也一样
    message = bytes(str(servertime) + '\t' + str(nonce) + '\n' + str(pwd) , encoding = 'utf-8')
    sp = binascii.b2a_hex(rsa.encrypt(message , key))
    #=======================登录=======================
    #param就是激动人心的登陆post参数，这个参数用到了若干个上面第一步获取到的数据，可说的不多
    param = {'entry' : 'weibo' , 'gateway' : 1 , 'from' : '' , 'savestate' : 7 , 'useticket' : 1 , 'pagerefer' : 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D' , 'vsnf' : 1 , 'su' : su , 'service' : 'miniblog' , 'servertime' : servertime , 'nonce' : nonce , 'pwencode' : 'rsa2' , 'rsakv' : rsakv , 'sp' : sp , 'sr' : '1680*1050' ,
             'encoding' : 'UTF-8' , 'prelt' : 961 , 'url' : 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'}
    # 这里就是使用postData的唯一一处，也很简单
    s = postData('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)' , param)
    # 好了，当你的代码执行到这里时，已经完成了大部分了，可是有很多爬虫童鞋跟我一样还就栽在了这里，假如你跳过这里直接去执行获取粉丝的这几行代码你就会发现你获取的到还是让你登陆的页面，真郁闷啊，我就栽在这里长达一天啊
    # 好了，我们还是继续。这个urll是登陆之后新浪返回的一段脚本中定义的一个进一步登陆的url，之前还都是获取参数和验证之类的，这一步才是真正的登陆，所以你还需要再一次把这个urll获取到并用get登陆即可
    urll = re.findall("location.replace\(\'(.*?)\'\);" , s)[0]
    getData(urll)
    #======================获取粉丝====================
    # 如果你没有跳过刚才那个urll来到这里的话，那么恭喜你！你成功了，接下来就是你在新浪微博里畅爬的时候了，获取到任何你想获取到的数据了！
    # 可以尝试着获取你自己的微博主页看看，你就会发现那是一个多大几百kb的文件了


