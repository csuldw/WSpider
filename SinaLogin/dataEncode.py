# -*- coding: utf-8 -*-
"""
Created on Tue Nov 08 10:14:38 2016

@author: liudiwei
"""
import base64
import rsa
import binascii
import requests
import json
import re

#使用base64对用户名进行编码
def encode_username(username):
    return base64.encodestring(username)[:-1]
    
#使用rsa2对password进行编码
def encode_password(password, servertime, nonce, pubkey):
    rsaPubkey = int(pubkey, 16)
    RSAKey = rsa.PublicKey(rsaPubkey, 65537) #创建公钥
    codeStr = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #根据js拼接方式构造明文
    pwd = rsa.encrypt(codeStr, RSAKey)  #使用rsa进行加密
    return binascii.b2a_hex(pwd)  #将加密信息转换为16进制。

#读取preinfo.php，获取servertime, nonce, pubkey, rsakv四个参数值
def get_prelogin_info():
    url = r'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)'
    html = requests.get(url).text
    jsonStr = re.findall(r'\((\{.*?\})\)', html)[0]
    data = json.loads(jsonStr)
    servertime = data["servertime"]
    nonce = data["nonce"]
    pubkey = data["pubkey"]
    rsakv = data["rsakv"]
    return servertime, nonce, pubkey, rsakv

#根据Fiddler抓取的数据，构造post_data
def encode_post_data(username, password, servertime, nonce, pubkey, rsakv):
    su = encode_username(username)
    sp = encode_password(password, servertime, nonce, pubkey)
    #用于登录到 http://login.sina.com.cn
    post_data = {
        "cdult" : "3",
        "domain" : "sina.com.cn",
        "encoding" : "UTF-8",
        "entry" : "account",
        "from" : "",
        "gateway" : "1",
        "nonce" : nonce,
        "pagerefer" : "http://login.sina.com.cn/sso/logout.php",
        "prelt" : "41",
        "pwencode" : "rsa2",
        "returntype" : "TEXT",
        "rsakv" : rsakv,
        "savestate" : "30",
        "servertime" : servertime,
        "service" : "sso",
        "sp" : sp,
        "sr" : "1366*768",
        "su" : su,
        "useticket" : "0",
        "vsnf" : "1"
    }
    #用于登录到 http://login.sina.com.cn/signup/signin.php?entry=ss
    """
    post_data = {
        "cdult" : "3",
        "domain" : "sina.com.cn",
        "encoding" : "UTF-8",
        "entry" : "sso",
        "from" : "null",
        "gateway" : "1",
        "pagerefer" : "",
        "prelt" : "0",
        "returntype" : "TEXT",
        "savestate" : "30",
        "service" : "sso",
        "sp" : password,
        "sr" : "1366*768",
        "su" : su,
        "useticket" : "0",
        "vsnf" : "1"
    }    
    """
    return post_data

#设置请求时的headers
headers = {
    "Origin" : "https://login.sina.com.cn",
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36",
    "Content-Type" : "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer" : "https://login.sina.com.cn/signup/signin.php?entry=sso",
    "Accept-Encoding" : "deflate, br",
    "Accept-Language" : "en-GB,en;q=0.8,zh-CN;q=0.6,zh;q=0.4"
}