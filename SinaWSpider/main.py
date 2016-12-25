# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 11:08:52 2016

@author: liudiwei
"""

import SinaSpider as slib
import myconf
import json
import random
import pymongo

#初始化MongoDB
def initMongoClient():
    conn = pymongo.MongoClient("localhost", 27017)
    print "Connected to Mongodb!"
    db = conn.sina_db
    return db

def spiderSinaData(session, db, uid):
    uidlist = [] 
    try:
        collection = db.userinfo
        if collection.find_one({"uid": uid}) == None:
            session.switchUserAccount(myconf.userlist)        
            userinfo = session.getUserInfos(uid)    
            session.output(json.dumps(userinfo), "output/%s/%s_info.json" %(uid, uid)) 
            collection.insert(userinfo)
        
        session.switchUserAccount(myconf.userlist)
        follows = session.getUserFollows(uid)
        session.output(json.dumps(follows), "output/%s/%s_follows.json" %(uid, uid)) 
        collection = db.follows
        if collection.find_one({"uid": uid}) == None:    
            collection.insert(follows)
            
        session.switchUserAccount(myconf.userlist)
        fans = session.getUserFans(uid)
        session.output(json.dumps(fans), "output/%s/%s_fans.json" %(uid, uid)) 
        collection = db.fans
        if collection.find_one({"uid": uid}) == None:    
            collection.insert(fans)
        
        user_tweets = []
        session.getUserTweets(uid, user_tweets)
        collection = db.tweets
        for elem in user_tweets:
            if collection.find_one(elem) == None:
                collection.insert(json.loads(elem))

        uidlist = list(set(uidlist).union(fans["fans_ids"]).union(follows["follow_ids"]))
    except Exception,e:
        session.logger.error("spiderSinaData Exception! -->" + str(e) )
        return []
    return uidlist

def main():
    db = initMongoClient()
    client = slib.SinaClient()
    session = client.switchUserAccount(myconf.userlist)
    uidpool = ["2006647941"] 
    cnt = 0
    while len(uidpool):
        uid = random.choice(uidpool)
        cnt += 1
        session.logger.info("scraping " + str(cnt) + "th user, uid is " + uid)
        uidlist = spiderSinaData(session, db, uid)
        uidpool = list(set(uidpool).union(uidlist))
        session.output("\n".join(uidlist), "output/uidlist/%s_uids.data" %uid)
        uidpool.remove(uid)
        session.logger.info("uidpool size: " + str(len(uidpool)))
    return cnt

#不使用MongoDB，直接将结果保存到本地
def test():
    client = slib.SinaClient()
    session = client.switchUserAccount(myconf.userlist)
    uidpool = ["3873827550", "1656209093", "1669282904"] #qianyi me
    cnt = 0
    while len(uidpool):
        uid = random.choice(uidpool)
        cnt += 1
        session.logger.info("scraping " + str(cnt) + "th user, uid is " + uid)
        userinfo = session.getUserInfos(uid)    
        session.output(json.dumps(userinfo), "output/%s/%s_info.json" %(uid, uid))
        uidpool.remove(uid)
            
if __name__ == '__main__':
    #保存至MongoDB 调用main方法，只保存本地调用test方法
    test()
    