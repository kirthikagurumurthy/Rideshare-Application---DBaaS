import pika
import json
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps
from subprocess import check_output
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

client = MongoClient("mongodb://sync-mongo:27017")

connection_s = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
channel_s = connection_s.channel()
channel_s.queue_declare(queue="syncq")

class SyncQ(object):
    total  = 0

    def sync_func(self):
        self.total+=1
        print("######### NOW SYNCING /#######")
        db = client.uber
        connection_sync = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
        channel_sync = connection_sync.channel()
        channel_sync.exchange_declare(exchange='logs', exchange_type='fanout')
        commands = dumps(db.logs.find())
        channel_sync.basic_publish(exchange='logs', routing_key='', body=commands)

class Callback(object):
    def __init__(self):
        self.count=0

    def sync_callback(self,ch, method, properties, body):
        self.count+=1
        db = client.uber
        print("[x] received %r" %body)
        d_values = json.loads(body)    
        db.logs.insert(d_values)
        if(self.count>2):               #confirm number needed
            scheduler = BackgroundScheduler()
            scheduler.add_job(func=S.sync_func, trigger="interval", seconds=1)
            scheduler.start()  
            atexit.register(lambda: scheduler.shutdown())
            #print("######### NOW SYNCING /#######")
            #db = client.uber
            #connection_sync = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
            #channel_sync = connection_sync.channel()
            #channel_sync.exchange_declare(exchange='logs', exchange_type='fanout')
            #commands = dumps(db.logs.find())
            #channel_sync.basic_publish(exchange='logs', routing_key='', body=commands)
        if(self.count>=1):
            print("######### NOW SYNCING /#######")
            db = client.uber
            connection_sync = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
            channel_sync = connection_sync.channel()
            channel_sync.exchange_declare(exchange='logs', exchange_type='fanout')
            commands = dumps(db.logs.find())
            channel_sync.basic_publish(exchange='logs', routing_key='', body=commands)


S = SyncQ()
C = Callback()
channel_s.basic_consume(queue="syncq", on_message_callback=C.sync_callback, auto_ack=True)
print("Waiting for syncq messages")
channel_s.start_consuming() 
