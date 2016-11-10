# -*- coding: utf-8 -*-
"""
Created on Thu Nov 02 14:01:17 2016

@author: liudiwei
"""
import os
import urllib
import urllib2
import cookielib
import logging  
import re

class WSpider(object):
    def __init__(self):
        #init params
        self.url_path = None
        self.post_data = None
        self.header = {}
        self.domain = None
        self.operate = None
        self.logger = None
        #init cookie
        self.cookiejar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        urllib2.install_opener(self.opener)

    def setRequestData(self, url_path=None, post_data=None, header=None):
        self.url_path = url_path
        self.post_data = post_data
        self.header = header

    def sendRequest(self, url, data={}, header={}):
        request = urllib2.Request(url, urllib.urlencode(data), header)
        result = urllib2.urlopen(request)
        return result

    def getHtmlText(self, is_cookie=False):
        if self.post_data == None and self.header == {}:
            request = urllib2.Request(self.url_path)
        elif self.post_data == None:
            request = urllib2.Request(self.url_path, headers = self.header)
        else:
            request = urllib2.Request(self.url_path, urllib.urlencode(self.post_data), self.header)
        result = urllib2.urlopen(request)
        if is_cookie: 
            self.operate = self.opener.open(request)
        resText = result.read()
        return resText 

    """
    Save captcha to local    
    """    
    def saveCaptcha(self, captcha_url, outpath, save_mode='wb'):
        picture = self.opener.open(captcha_url).read() #用openr访问验证码地址,获取cookie
        self.mkdirs(outpath)
        local = open(outpath, save_mode)
        local.write(picture)
        local.close()    
        
    def getHtml(self, url):
        page = urllib.urlopen(url)
        html = page.read()
        return html

    """
    功能：将文本内容输出至本地
    @params 
        content：文本内容
        out_path: 输出路径
    """
    def output(self, content, out_path, save_mode="w"):
        self.mkdirs(out_path)
        fw = open(out_path, save_mode)
        fw.write(content)
        fw.close()

    """#EXAMPLE 
    logger = createLogger('mylogger', 'temp/logger.log')
    logger.debug('logger debug message')  
    logger.info('logger info message')  
    logger.warning('logger warning message')  
    logger.error('logger error message')  
    logger.critical('logger critical message')  
    """    
    def createLogger(self, logger_name, log_file):
        self.mkdirs(log_file)
        # 创建一个logger
        logger = logging.getLogger(logger_name)  
        logger.setLevel(logging.INFO)  
        # 创建一个handler，用于写入日志文件    
        fh = logging.FileHandler(log_file)  
        # 再创建一个handler，用于输出到控制台    
        ch = logging.StreamHandler()  
        # 定义handler的输出格式formatter    
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')  
        fh.setFormatter(formatter)  
        ch.setFormatter(formatter)  
        # 给logger添加handler    
        logger.addHandler(fh)  
        logger.addHandler(ch)
        self.logger = logger
        return logger

    def mkdirs(self, log_file):
        prefix = os.path.dirname(log_file)
        if not os.path.exists(prefix):
            os.makedirs(prefix)
    
    #在html中解析重定位结果部分函数
    def sRedirectData(self, text):
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        loginUrl = p.search(text).group(1)
        return loginUrl