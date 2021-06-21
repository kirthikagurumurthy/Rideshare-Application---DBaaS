import pika
import json
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps
from subprocess import check_output
import os

client = MongoClient("mongodb://master-mongo:27017")

connection_s = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
channel_s = connection_s.channel()
channel_s.queue_declare(queue="syncq")

def write_callback(ch,method,properties,body):
    db = client.uber
    print("[x] received %r" %body)
    d_values = json.loads(body)
    collection = d_values["collection"]
    data = d_values["data"]
    method = d_values["method"]

    if(collection=="rides"):
        if(method=="post"):
            db.rides.insert(data)
        if(method=="join"):
            rideId = d_values["rideId"]
            db.rides.update({"rideId":rideId},{'$push':data})
        if(method=="delete"):
            db.rides.remove(data)
        if(method=="clear"):
            db.rides.remove({})

    if(collection=="users"):
        if(method=="put"):
            db.users.insert(data)
        if(method=="delete"):
            db.users.remove(data)
        if(method=="clear"):
            db.users.remove({})	

    channel_s.basic_publish(exchange='',routing_key='syncq',body=body)
    print("[x] published to syncq",body)
    


connection_w = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
channel_w = connection_w.channel()
channel_w.queue_declare(queue="writeq")


channel_w.basic_consume(queue="writeq", on_message_callback=write_callback, auto_ack=True)
print("Waiting for write messages")
channel_w.start_consuming() 
