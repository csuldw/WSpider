from datetime import datetime, timedelta
from pymongo import MongoClient, errors

class MongoQueue(object):
    WAITING, PROCESSING, COMPLETE = range(3)

    def __init__(self, conn=None, timeout=1000):
        self.conn = MongoClient("localhost", 27017) if conn is None else conn
        self.db = self.conn.sina_db
        self.timeout = timeout
        self.collection = self.db.uid_queue

    def __nonzero__(self):
        record = self.collection.find_one({"status" : {"$ne": self.COMPLETE}})
        return True if record else False

    def push(self, uid):
        try:
            self.collection.insert({'_id': uid, 'status': self.WAITING})
        except errors.DuplicateKeyError as e:
            print e            
            pass

    def pop(self):
        record = self.collection.find_and_modify(
                query={'status': self.WAITING}, 
                update={'$set': {'status': self.PROCESSING, 'timestamp': datetime.now()}}
            )
        if record:
            return record['_id']
        else:
            self.repair()

    def complete(self, uid):
        self.collection.update({'_id': uid}, {'$set': {'status': self.COMPLETE}})

    def repair(self):
        record = self.collection.find_and_modify(
            query = {
                'timestamp': {'$lt': datetime.now() - timedelta(seconds=self.timeout)}, 
                'status': {'$ne': self.COMPLETE}
            },
            update = {'$set': {'status': self.WAITING}}
        )
        if record:
            print 'Released uid', record['_id']