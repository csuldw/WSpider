# -*- coding: utf-8 -*-
"""
Created on Tue Nov 08 10:14:38 2016

@author: liudiwei
"""
import os
import json
import cookielib
import urllib
import urllib2
import re
import random
import time
import socket
from bs4 import BeautifulSoup as BS

import dataEncode
import myconf
from Logger import LogClient

import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
        #登录状态，初始化为False，表示未登录状态
        self.status = False
        #微博API必备信息
        self.access_token = None
        self.app_key = None
        #初始时调用initParams方法，初始化相关参数
        self.initParams()
        self.timeout = 3
        socket.setdefaulttimeout(3)
        self.tryTimes = 8

    #初始化参数
    def initParams(self):
        self.logger = LogClient().createLogger('SinaWSpider', myconf.log_out_path)
        self.headers = myconf.headers
        self.access_token = myconf.access_token
        self.app_key = myconf.app_key
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
    
    #使用用户代理，更换header中的User-Agent
    def switchUserAgent(self, enableAgent=True):
        user_agent = random.choice(myconf.agent_list)
        self.headers["User-Agent"] = user_agent
        return self

    #用于切换用户账号，防止长时间爬取账号被禁
    def switchUserAccount(self, userlist):
        is_login = False
        while not is_login: 
            self.switchUserAgent()
            self.logger.info("User-Agent is: " + self.headers["User-Agent"])
            user = random.choice(userlist).split("|")
            self.logger.info("logining with user: " + user[0])
            session = self.login(user[0], user[1])
            if not session.status:
                self.logger.info("Cannot login to sina!")
                continue
            is_login = True
        return self
    
    #生成Cookie,接下来的所有get和post请求都带上已经获取的cookie
    def enableCookie(self, enableProxy=False):
        self.cookiejar = cookielib.LWPCookieJar()  # 建立COOKIE
        cookie_support = urllib2.HTTPCookieProcessor(self.cookiejar)
        if enableProxy:
            proxy = myconf.swithProxy()
            proxy_support = urllib2.ProxyHandler(proxy) # 使用代理myconf.proxies
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            self.logger.info("Proxy enable, proxy is: " + str(proxy))
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        return self
    
    #使用urllib2模拟登录过程
    def login(self, username=None, password=None):
        self.status = False #重新将登录状态设置为False
        self.logger.info("Start to login...")
        #根据用户名和密码给默认参数赋值,并初始化post_data
        self.setAccount(username, password) 
        self.setPostData()
        self.enableCookie(enableProxy=True)
        #登录时请求的url
        login_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        headers = self.headers
        try:  
            request = urllib2.Request(login_url, urllib.urlencode(self.post_data), headers)
            resText = urllib2.urlopen(request).read()
            jsonText = json.loads(resText)
            if jsonText["retcode"] == "0":
                self.logger.info("Login success!")
                self.status = True
                #将cookie加入到headers中
                cookies = ';'.join([cookie.name + "=" + cookie.value for cookie in self.cookiejar])
                headers["Cookie"] = cookies
            else:
                self.logger.error("Login Failed --> " + jsonText["reason"])
        except Exception, e:
            self.logger.error("Login Failed2! --> " + str(e))
        self.headers = headers
        return self
    
    #打开url时携带headers,此header需携带cookies
    def openURL(self, url, data=None, tryTimes=1):
        text = ""
        if tryTimes < self.tryTimes:
            try:
                self.logger.info("open url %s times: %s" %(str(tryTimes), url))
                req = urllib2.Request(url, data=data, headers=self.headers)
                text = urllib2.urlopen(req).read()
            except Exception, e:
                self.logger.error("openURL error, " + str(e))
                self.switchUserAccount(myconf.userlist)
                text = self.openURL(url, data=data, tryTimes = tryTimes+1)
        return text #self.unzip(text)
    
    #功能：将文本内容输出至本地
    def output(self, content, out_path, save_mode="w"):
        self.logger.info("Save page to: " + out_path)
        prefix = os.path.dirname(out_path)
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        fw = open(out_path, save_mode)
        fw.write(content)
        fw.close()
        return self
    
    """
    @Desc:使用微博API:待完善
    Access Token: 2.00ojIyoBWed7FC573b7abad1geUrOE
    app_key: 1912496300  
    说明：API接口限制太多，很多接口只能获取当前登录用户的信息，无法获取好友的信息，所以干脆放弃了
    """    
    #************************************************************************** 
    def getApiJSONData(self, url, params, post_data=None):
        cmb_params = '&'.join([x + "=" + str(params[x]) for x in params.keys()])
        url += "?" + cmb_params 
        req = urllib2.Request(url, data=post_data, headers=self.headers)
        text = urllib2.urlopen(req).read()
        return self.unzip(text)
    
    #使用微博API获取用户信息
    def getUserInfo(self, uid):
        url = "https://api.weibo.com/2/users/show.json"
        params = {"access_token": self.access_token, "uid": uid}
        jsonRes = self.getApiJSONData(url, params)
        self.output(jsonRes, "output/" + uid + ".json")
        return jsonRes
    
    #获取用户关注对象UID列表 friendship/friends/ids
    def getFriendUidList(self, uid):
        url = "https://api.weibo.com/2/friendships/friends.json"
        params = {"access_token": self.access_token, "uid": uid}
        jsonRes = self.getApiJSONData(url, params)
        self.output(jsonRes, "output/" + uid + ".json")
        return jsonRes
        
    #**************************************************************************
    #获取用户个人信息
    def getUserInfos(self, uid):
        url_app = "http://weibo.cn/%s/info" %uid
        text_app = self.openURL(url_app)
        soup_app = unicode(BS(text_app, "html.parser"))
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?)<br', soup_app)  # 昵称
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?)<br', soup_app)  # 性别
        address = re.findall(u'\u5730\u533a[:|\uff1a](.*?)<br', soup_app)  # 地区（包括省份和城市）
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?)<br', soup_app)  # 生日
        desc = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?)<br', soup_app)  # 简介
        sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?)<br', soup_app)  # 性取向
        marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?)<br', soup_app)  # 婚姻状况
        homepage = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?)<br', soup_app)  #首页链接
        #根据app主页获取数据
        app_page = "http://weibo.cn/%s" %uid
        text_homepage = self.openURL(app_page)
        soup_home = unicode(BS(text_homepage, "html.parser"))
        tweets_count = re.findall(u'\u5fae\u535a\[(\d+)\]', soup_home)
        follows_count = re.findall(u'\u5173\u6ce8\[(\d+)\]', soup_home)
        fans_count = re.findall(u'\u7c89\u4e1d\[(\d+)\]', soup_home)
        #根据web用户详情页获取注册日期
        url_web = "http://weibo.com/%s/info" %uid
        text_web = self.openURL(url_web)
        reg_date = re.findall(r"\d{4}-\d{2}-\d{2}", text_web)
        #根据标签详情页获取标签        
        tag_url = "http://weibo.cn/account/privacy/tags/?uid=%s" %uid
        text_tag = self.openURL(tag_url)      
        soup_tag = BS(text_tag, "html.parser")
        res = soup_tag.find_all('div', {"class":"c"})
        tags = "|".join([elem.text for elem in res[2].find_all("a")])
        
        #将用户信息合并        
        userinfo = {}
        userinfo["uid"] = uid
        userinfo["nickname"] = nickname[0] if nickname else ""
        userinfo["gender"] = gender[0] if gender else ""
        userinfo["address"] = address[0] if address else ""
        userinfo["birthday"] = birthday[0] if birthday else ""
        userinfo["desc"] = desc[0] if desc else ""
        userinfo["sex_orientation"] = sexorientation[0] if sexorientation else ""
        userinfo["marriage"] = marriage[0] if marriage else ""
        userinfo["homepage"] = homepage[0] if homepage else ""
        userinfo["tweets_count"] = tweets_count[0] if tweets_count else "0"
        userinfo["follows_count"] = follows_count[0] if follows_count else "0"
        userinfo["fans_count"] = fans_count[0] if fans_count else "0"
        userinfo["reg_date"] = reg_date[0] if reg_date else ""
        userinfo["tags"] = tags if tags else ""
        return userinfo

    #爬取单个用户的follow，ulr = http://weibo.cn/%uid/follow?page=1
    def getUserFollows(self, uid, params="page=1"):
        time.sleep(2)
        self.switchUserAgent()
        url = "http://weibo.cn/%s/follow?%s" %(uid, params)
        text = self.openURL(url)
        soup = BS(text, "html.parser")
        res = soup.find_all('table')
        reg_uid = r"uid=(\d+)&" 
        follows = {"uid": uid, "follow_ids": list(set([y for x in [re.findall(reg_uid, str(elem)) for elem in res] for y in x ]))}
        next_url = re.findall('<div><a href="(.*?)">下页</a>&nbsp', text) #匹配"下页"内容
        if len(next_url) != 0:
            url_params = next_url[0].split("?")[-1] 
            if url_params != params:
                follows['follow_ids'].extend(self.getUserFollows(uid, params=url_params)["follow_ids"]) #将结果集合并
        return follows
    
    #获取用户粉丝对象UID列表 ulr = http://weibo.cn/%uid/fan?page=1
    def getUserFans(self, uid, params="page=1"):
        time.sleep(2)
        self.switchUserAgent()
        url = "http://weibo.cn/%s/fans?%s" %(uid, params)
        text = self.openURL(url)
        soup = BS(text, "html.parser")
        res = soup.find_all('table')
        reg_uid = r"uid=(\d+)&"
        fans = {"uid": uid, "fans_ids": list(set([y for x in [re.findall(reg_uid, str(elem)) for elem in res] for y in x ]))}
        next_url = re.findall('<div><a href="(.*?)">下页</a>&nbsp', text) #匹配"下页"内容
        if len(next_url) != 0:
            url_params = next_url[0].split("?")[-1]
            if url_params != params:
                fans['fans_ids'].extend(self.getUserFans(uid, params=url_params)["fans_ids"]) #将结果集合并
        return fans
        
    #获取用户的发的微博信息
    def getUserTweets(self, uid, tweets_all, params="page=1"):
        self.switchUserAccount(myconf.userlist)
        url = r"http://weibo.cn/%s/profile?%s" %(uid, params)
        text = self.openURL(url)
        soup = BS(text, "html.parser")
        res = soup.find_all("div", {"class":"c"})
        #规则：如果div中子div数量为1，则为一个原厂文本说说；数量为2，则根据cmt判断是原创图文还是转发文本说说；数量为3，则为转发图文
        tweets_list = []
        for elem in res:
            tweets = {}
            unicode_text = unicode(elem)
            sub_divs = elem.find_all("div")
            today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            if len(sub_divs) in [1, 2, 3]:
                tweets["uid"] = uid
                tweets["reason"] = "null"
                tweets["content"] = elem.find("span", {"class": "ctt"}).text
                soup_text = elem.find("span", {"class": "ct"}).text
                created_at = re.findall("\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d", unicode(soup_text))
                post_time = re.findall("\d\d:\d\d", unicode(soup_text))
                split_text = unicode(soup_text).split(u"\u5206\u949f\u524d")
                if not created_at:
                    created_at = re.findall(u"\d\d\u6708\d\d\u65e5 \d\d:\d\d", unicode(soup_text))
                    tweets["created_at"] = time.strftime("%Y-",time.localtime()) + unicode(created_at[0]).replace(u"\u6708", "-").replace(u"\u65e5", "") + ":00"
                    tweets["source"] = soup_text.split(created_at[0])[-1].strip(u"\u00a0\u6765\u81ea")
                elif created_at:
                    tweets["created_at"] = unicode(created_at[0]).replace(u"\u6708", "-").replace(u"\u65e5", "")
                    tweets["source"] = soup_text.split(created_at[0])[-1].strip(u"\u00a0\u6765\u81ea")
                elif post_time:
                    tweets["created_at"] = today + " " + post_time[0] + ":00"
                    tweets["source"] = soup_text.split(post_time[0])[-1].strip(u"\u00a0\u6765\u81ea")
                elif len(split_text) == 2:
                    tweets["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(split_text[0])*60))
                    tweets["source"] = split_text[-1].strip(u"\u00a0\u6765\u81ea")
                tweets["like_count"] = re.findall(u'\u8d5e\[(\d+)\]', unicode_text)[-1]
                tweets["repost_count"] = re.findall(u'\u8f6c\u53d1\[(\d+)\]', unicode_text)[-1]
                tweets["comment_count"] = re.findall( u'\u8bc4\u8bba\[(\d+)\]', unicode_text)[-1]
            if len(sub_divs) == 0:
                pass
            elif len(sub_divs) == 1:
                tweets["type"] = "original_text"
            elif len(sub_divs) == 2:
                tweets["type"] = "original_image"
                #根据cmt的存在判断是否为转发的文字和原创的图文说说
                cmt = elem.find_all("span", {"class": "cmt"})
                if cmt: 
                    tweets["type"] = "repost_text"
                    tweets["reason"] = re.findall("</span>(.*?)<a", str(sub_divs[1]))[0]
            elif len(sub_divs) == 3:
                tweets["type"] = "repost_image"
                tweets["reason"] = re.findall("</span>(.*?)<a", str(sub_divs[2]))[0]
            else:
                self.logger.error("parse error")
                pass
            if tweets:
                tweets_list.append(json.dumps(tweets))
        #self.output("\n".join(tweets_list), "output/" + uid + "/" + uid + "_tweets_" + params.replace("=", "") + ".json")
        tweets_all.extend(tweets_list)

        next_url = re.findall('<div><a href="(.*?)">下页</a>&nbsp', text) #匹配"下页"内容
        if len(next_url) != 0 and len(tweets_all) < 200:
            url_params = next_url[0].split("?")[-1]
            if url_params != params:
                self.getUserTweets(uid, tweets_all, params=url_params)
        return tweets_list
