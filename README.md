# Introduction

- SinaWSpider：Mini爬虫爬取新浪数据，详细步骤参见[新浪微博数据爬取Part 3：小爬虫的诞生](http://www.csuldw.com/2016/12/25/2016-12-25-sina-spider-user-data-part3/)
- SinaLogin：模拟登录新浪微博，详细步骤参见[模拟新浪微博登录-原理分析到实现](http://www.csuldw.com/2016/11/10/2016-11-10-simulate-sina-login/)
- ZhiHuPro：模拟登录知乎网，详细内容参见：[小试牛刀：使用Python模拟登录知乎](http://www.csuldw.com/2016/11/05/2016-11-05-simulate-zhihu-login/)，

# 子项目

## Mini小爬虫

- conf.ini：用于配置proxies、headers等参数，其中Sina API的参数需设置成自己的；
- dataEncode.py：用于模拟登录sina时提交的POST数据；
- Logger.py：用于输出日志文件；
- main.py：运行项目的入口文件；
- myconf.py：加载配置文件；
- SinaSpider.py：spider核心内容，主要是SinaClient类，内部方法说明如下
	- switchUserAccount(self, userlist)：用于切换用户账号，防止长时间爬取账号被禁
	- login(self, username, password)：根据用户名和密码登录sina微博
	- getUserInfos(self, uid)：根据用户ID获取用户个人信息
	- getUserFollows(self, uid, params)：根据用户ID 获取用户关注的用户ID列表
	- getUserFans(self, uid, params)：根据用户ID 获取粉丝ID列表
	- getUserTweets(self, uid, tweets_all, params)：根据用户ID 获取微博，tweets_all是一个list变量
- output：输出目录

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