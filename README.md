# Introduction

- SinaWSpider：Mini爬虫爬取新浪数据，详细步骤参见[新浪微博数据爬取Part 3：小爬虫的诞生](http://www.csuldw.com/2016/12/25/2016-12-25-sina-spider-user-data-part3/)
- SinaLogin：模拟登录新浪微博，详细步骤参见[模拟新浪微博登录-原理分析到实现](http://www.csuldw.com/2016/11/10/2016-11-10-simulate-sina-login/)
- ZhiHuPro：模拟登录知乎网，详细内容参见：[小试牛刀：使用Python模拟登录知乎](http://www.csuldw.com/2016/11/05/2016-11-05-simulate-zhihu-login/)，

# 子项目

## 模拟登录知乎

文件介绍

- ZhiHuPro/zhiHuLogin.py
- ZhiHuPro/WSpider.py：封装的WSpider类，包括日志输出函数
- ZhiHuPro/out：存放输出的网页
- ZhiHuPro/temp：存放验证码

## 模拟登录新浪

文件介绍

- SinaLogin/dataEncode.py：用于对提交POST请求的数据进行编码处理
- SinaLogin/Logger.py：用于打印log
- SinaLogin/SinaSpider.py：用于爬取sina微博数据的文件（主文件）
- SinaLogin/out：用于存储输出文件

## Contributor

@author： [Diwei Liu](http://www.csuldw.com/about/)

---

此项目将在后续持续更新，敬请关注，喜欢就给个Star吧。