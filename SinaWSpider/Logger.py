# -*- coding: utf-8 -*-
"""
Created on Thu Nov 02 14:01:17 2016

@author: liudiwei
"""
import os
import logging  

class LogClient(object):
    def __init__(self):
        self.logger = None

    """#EXAMPLE 
    logger = createLogger('mylogger', 'temp/logger.log')
    logger.debug('logger debug message')  
    logger.info('logger info message')  
    logger.warning('logger warning message')  
    logger.error('logger error message')  
    logger.critical('logger critical message')  
    """    
    def createLogger(self, logger_name, log_file):
        prefix = os.path.dirname(log_file)
        if not os.path.exists(prefix):
            os.makedirs(prefix)
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
        return self.logger