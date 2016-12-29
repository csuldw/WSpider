欢迎使用SinaWSpider爬虫，同步教程请参阅：[新浪微博数据爬取Part 3：小爬虫的诞生](http://www.csuldw.com/2016/12/25/2016-12-25-sina-spider-user-data-part3/)。

# 20161228更新

- 修改conf.ini文件，删除proxy变量；
- 修改myconf.py，将proxy_pool从文件中读取，同时修改swithProxy()方法；
- 增加MongoQueue.py文件，使用mongodb作为队列
- 增加proxy目录，子目录spiderProxypy为爬取代理的代码，最终内容写入到当前的proxy.data中；
- 修改main.py，增加多进程执行代码，进程数量为CPU个数；

---

# 20161225

## 文件说明

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

## 结果说明

1.getUserInfos可获取用户下列信息

```
uid:用户ID
nickname:昵称
address:地址
sex:性别
birthday:生日
desc:简介
marriage:婚姻状况
follows_count:关注数
fans_count:粉丝数
tweets_count:微博数
homepage:首页链接
reg_date:注册时间
tag:标签
sex_orientation:性取向
```

2.getUserFollows可获取用户关注人列表

```
uid：用户ID
follow_ids：关注人ID
```

3.getUserFans 可获取用户粉丝列表

```
uid：用户ID
fans_ids粉丝
```   

4.getUserTweets方法可获取用户下列微博信息

```
uid：用户ID
content：微博内容
created_at：发表时间
source：发布工具/平台
comment_count：评论数
repost_count：转载数
type：微博类型（原创/转发）
like_count：点赞量
reason：转发理由（原创博文无理由取值为空）
```

## Contributor

@author： [Diwei Liu](http://www.csuldw.com/about/)

---

目前该爬虫正处于成长阶段，部分功能尚未完善，需进行进一步优化，如果感兴趣，可关注博主的微博[@拾毅者](http://weibo.com/liudiwei210)，期待下个路口遇见你。

喜欢就给个star吧~
