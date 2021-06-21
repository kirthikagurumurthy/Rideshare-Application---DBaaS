import pika
import json
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps
from subprocess import check_output
import os

mongo = os.environ["MONGO"]

client = MongoClient("mongodb://"+mongo+":27017")

connection_sync = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat=0))
channel_sync = connection_sync.channel()

channel_sync.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel_sync.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel_sync.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs')
filename = "logs"+mongo.partition("slave-mongo")[2]+".txt"
logs_file = open(filename,"w")
logs_file.close()

def callback(ch, method, properties, body):
    db = client.uber
    print(" [x] %r" % body)                     
    filename = "logs"+mongo.partition("slave-mongo")[2]+".txt"
    logs_file = open(filename,"r+")       #file to track updates
    logs = logs_file.read().split()
    print("##############################################################",logs)
    command_list = json.loads(body)
    for command in command_list:
        if(command['_id']["$oid"] not in logs):
            logs_file.write(command['_id']["$oid"]+"\n")

            collection = command["collection"]
            data = command["data"]
            method = command["method"]

            if(collection=="rides"):
                if(method=="post"):
                    db.rides.insert(data)
                if(method=="join"):
                    rideId = command["rideId"]
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

    logs_file.close()
    print("Database Update Successfull!!")


    

channel_sync.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel_sync.start_consuming()
