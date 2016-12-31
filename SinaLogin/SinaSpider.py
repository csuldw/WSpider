# -*- coding: utf-8 -*-
"""
Created on Tue Nov 08 10:14:38 2016

@author: liudiwei
"""
import os
import getpass
import json
import requests
import cookielib
import urllib
import urllib2
import gzip
import StringIO
import time

import dataEncode
from Logger import LogClient

class SinaClient(object):
    def __init__(self, username=None, password=None):
        #用户输入的用户名与密码
        self.username = username
        self.password = password
        #从prelogin.php中获取的数据
        self.servertime = None
        self.nonce = None
        self.pubkey = None
        self.rsakv = None
        #请求时提交的数据列表
        self.post_data = None
        self.headers = {}
        #用于存储登录后的session
        self.session = None   
        self.cookiejar = None
        #用于输出log信息
        self.logger = None
        #存储登录状态，初始状态为False        
        self.state = False
        #初始时调用initParams方法，初始化相关参数
        self.initParams()
    
    #初始化参数
    def initParams(self):
        self.logger = LogClient().createLogger('SinaClient', 'out/log_' + time.strftime("%Y%m%d", time.localtime()) + '.log')
        self.headers = dataEncode.headers
        return self
    
    #设置username 和 password
    def setAccount(self, username, password):
        self.username = username
        self.password = password
        return self
    
    #设置post_data
    def setPostData(self):
        self.servertime, self.nonce, self.pubkey, self.rsakv = dataEncode.get_prelogin_info()
        self.post_data = dataEncode.encode_post_data(self.username, self.password, self.servertime, self.nonce, self.pubkey, self.rsakv)
        return self
        
    #使用requests库登录到 https://login.sina.com.cn
    def login(self, username=None, password=None):
        #根据用户名和密码给默认参数赋值,并初始化post_data
        self.setAccount(username, password) 
        self.setPostData()
        #登录时请求的url
        login_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        session = requests.Session()
        response = session.post(login_url, data=self.post_data)
        json_text = response.content.decode('gbk')
        res_info = json.loads(json_text)
        try:
            if res_info["retcode"] == "0":
                self.logger.info("Login success!")
                self.state = True
                #把cookies添加到headers中
                cookies = session.cookies.get_dict()
                cookies = [key + "=" + value for key, value in cookies.items()]
                cookies = "; ".join(cookies)
                session.headers["Cookie"] = cookies
            else:
                self.logger.error("Login Failed! | " + res_info["reason"])
        except Exception, e:
            self.logger.error("Loading error --> " + e)
        self.session = session
        return session
    
    #生成Cookie,接下来的所有get和post请求都带上已经获取的cookie
    def enableCookie(self, enableProxy=False):
        self.cookiejar = cookielib.LWPCookieJar()  # 建立COOKIE
        cookie_support = urllib2.HTTPCookieProcessor(self.cookiejar)
        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http': 'http://122.96.59.107:843'}) # 使用代理
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            self.logger.info("Proxy enable.")
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    
    #使用urllib2模拟登录过程
    def login2(self, username=None, password=None):
        self.logger.info("Start to login...")
        #根据用户名和密码给默认参数赋值,并初始化post_data
        self.setAccount(username, password) 
        self.setPostData()
        self.enableCookie()
        #登录时请求的url
        login_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        headers = self.headers
        request = urllib2.Request(login_url, urllib.urlencode(self.post_data), headers)
        resText = urllib2.urlopen(request).read()
        try:        
            jsonText = json.loads(resText)
            if jsonText["retcode"] == "0":
                self.logger.info("Login success!")
                self.state = True
                #将cookie加入到headers中
                cookies = ';'.join([cookie.name + "=" + cookie.value for cookie in self.cookiejar])
                headers["Cookie"] = cookies
            else:
                self.logger.error("Login Failed --> " + jsonText["reason"])
        except Exception, e:
            print e
        self.headers = headers
        return self
    
    #打开url时携带headers,此header需携带cookies
    def openURL(self, url, data=None):
        req = urllib2.Request(url, data=data, headers=self.headers)
        text = urllib2.urlopen(req).read()
        return text
    
    #功能：将文本内容输出至本地
    def output(self, content, out_path, save_mode="w"):
        self.logger.info("Download html page to local machine. | path: " + out_path)
        prefix = os.path.dirname(out_path)
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        fw = open(out_path, save_mode)
        fw.write(content)
        fw.close()
        return self
        
    """
    防止读取出来的HTML乱码，测试样例如下
    req = urllib2.Request(url, headers=headers)
    text = urllib2.urlopen(req).read()
    unzip(text)
    """
    def unzip(self, data):
        data = StringIO.StringIO(data)
        gz = gzip.GzipFile(fileobj=data)
        data = gz.read()
        gz.close()
        return data    

#调用login1进行登录
def testLogin():
    client = SinaClient()
    username = raw_input("Please input username: ")
    password = getpass.getpass("Please input your password: ")   
    session = client.login(username, password)
    
    follow = session.post("http://weibo.cn/1669282904/follow").text.encode("utf-8")
    client.output(follow, "out/follow.html")


#调用login2进行登录
def testLogin2():
    client = SinaClient()
    username = raw_input("Please input username: ")
    password = getpass.getpass("Please input your password: ")   
    session = client.login2(username, password)
    
    info = session.openURL("http://weibo.com/1669282904/info")
    client.output(info, "out/info2.html")    
    
if __name__ == '__main__':
    testLogin()
    