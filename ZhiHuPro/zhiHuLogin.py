# -*- coding: utf-8 -*-
"""
Created on Thu Nov 02 17:07:17 2016

@author: liudiwei
"""
import os,sys
import urllib
from WSpider import WSpider
from bs4 import BeautifulSoup as BS
import getpass
import json

"""
2016.11.03 由于验证码问题暂时无法正常登陆
2016.11.04 成功登录，期间出现下列问题
验证码错误返回：{ "r": 1, "errcode": 1991829, "data": {"captcha":"验证码错误"}, "msg": "验证码错误" }
验证码过期：{ "r": 1, "errcode": 1991829, "data": {"captcha":"验证码回话无效 :(","name":"ERR_VERIFY_CAPTCHA_SESSION_INVALID"}, "msg": "验证码回话无效 :(" }
登录：{"r":0, "msg": "登录成功"}
"""
def zhiHuLogin():
    spy = WSpider()
    logger = spy.createLogger('mylogger', 'temp/logger.log')
    
    homepage = r"https://www.zhihu.com/"    
    html = spy.opener.open(homepage).read()
    soup = BS(html, "html.parser")
    _xsrf = soup.find("input", {'type':'hidden'}).get("value")

    #根据email和手机登陆得到的参数名不一样，email登陆传递的参数是‘email’，手机登陆传递的是‘phone_num’
    username = raw_input("Please input username: ")
    password = getpass.getpass("Please input your password: ")
    account_name = None
    if "@" in username:
        account_name = 'email'
    else:
        account_name = 'phone_num' 

    logger.info("save captcha to local machine.")
    captchaURL = r"https://www.zhihu.com/captcha.gif?type=login" #验证码url
    spy.saveCaptcha(captcha_url=captchaURL, outpath="temp/captcha.jpg")

    post_data = {
        '_xsrf': _xsrf,
        account_name: username,
        'password': password,
        'remember_me': 'true',
        'captcha':raw_input("Please input captcha: ")
    }
    header ={
        'Accept':'*/*' ,
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest',
        'Referer':'https://www.zhihu.com/',
        'Accept-Language':'en-GB,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'Accept-Encoding':'gzip, deflate, br',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
        'Host':'www.zhihu.com'
    }

    url = r"https://www.zhihu.com/login/" + account_name
    spy.setRequestData(url, post_data, header)
    resText = spy.getHtmlText()
    jsonText = json.loads(resText)

    if jsonText["r"] == 0:
        logger.info("Login success!")
    else:
        logger.error("Login Failed!")
        logger.error("Error info ---> " + jsonText["msg"])
        
    text = spy.opener.open(homepage).read()
    spy.output(text, "out/home.html")
    
if __name__ == '__main__':
    zhiHuLogin()