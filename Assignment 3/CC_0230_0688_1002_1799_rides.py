from flask import Flask, render_template,jsonify,request,abort
from flask_pymongo import PyMongo
import requests
import json
import re
from flask import Response
from bson.json_util import dumps
from datetime import datetime
import logging



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://rides-mongo:27017/rides"
mongo = PyMongo(app)

class counter(object):
    requests_count = 0

C = counter()
#API to create new ride
@app.route('/api/v1/rides',methods=['POST'])
def add_ride():
    C.requests_count+=1
    if(not request.json):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    data = request.get_json()
    username = request.get_json()["created_by"]
    #no_user = mongo.db.users.find({"username":username}).count()
    #print(username)
    header = {'Origin': '34.195.108.38'}
    users = requests.get('http://rides-share-ALB-1566032942.us-east-1.elb.amazonaws.com/api/v1/users', headers = header)
    users_list = json.loads(users.content.decode("utf-8"))
    no_user=0
    for record in users_list:
        if(record['username']==username):
            no_user+=1

    if(no_user==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        timestamp = request.get_json()["timestamp"]
        source = int(request.get_json()["source"])
        destination = int(request.get_json()["destination"])

        with open("AreaNameEnum.csv") as f:
            lines = sum(1 for line in f)
        if(source in range(1,199) and destination in range(1,199) and source!=destination):
            no_rides = mongo.db.rides.count()
            if(no_rides==0):
                rideId = 1
            else:
                rideId = list(mongo.db.rides.find())[no_rides-1]["rideId"]+1
            data= {"method":"post","collection":"rides","data":{"rideId":rideId,"created_by":username,"users":[],"timestamp":timestamp,"source":source,"dest$
            requests.post('http://127.0.0.1:5000/api/v1/db/write',json =data)
            return Response(json.dumps({}), status=201, mimetype='application/json')
        else:
            return Response(json.dumps({}), status=400, mimetype='application/json')



#API to get rides given source and destination as query params
@app.route('/api/v1/rides',methods=['GET'])
def list_rides():
    C.requests_count+=1
    source = request.args.get("source")
    destination = request.args.get("destination")
    with open("AreaNameEnum.csv") as f:
        lines = sum(1 for line in f)
    #print(lines)
    if(int(source) in range(1,lines) and int(destination) in range(1,lines) and int(source)!=int(destination)):
        data = {"method":"get_all","collection":"rides","data":{"source":int(source),"destination":int(destination)}}
        response = requests.post('http://127.0.0.1:5000/api/v1/db/read',json =data)
        if(json.loads(response.content.decode("utf-8"))==[]):
            return Response(json.dumps({}), status=204, mimetype='application/json')
        else:
            return(response.content)
    else:
        return Response(json.dumps({}), status=400, mimetype='application/json')


#API to get ride details given rideID in url
@app.route('/api/v1/rides/<int:rideId>',methods=['GET'])
def ride_details(rideId):
    C.requests_count+=1
    no_rides = mongo.db.rides.find({"rideId":rideId}).count()
    if(no_rides==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data = {"method":"get_ride","collection":"rides","data":{"rideId":rideId}}
        response = requests.post('http://127.0.0.1:5000/api/v1/db/read',json =data)
        return(response.content)



#API to add user to existing ride (join the ride)
@app.route('/api/v1/rides/<int:rideId>',methods=['POST'])
def join_ride(rideId):
    C.requests_count+=1
    no_rides = mongo.db.rides.find({"rideId":rideId}).count()
    data = request.get_json()
    username = request.get_json()["username"]
    #no_user = mongo.db.users.find({"username":username}).count()
    header = {'Origin': '34.195.108.38'}
    users = requests.get('http://rides-share-ALB-1566032942.us-east-1.elb.amazonaws.com/api/v1/users', headers = header)
    users_list = json.loads(users.content.decode("utf-8"))
    no_user=0
    for record in users_list:
        if(record['username']==username):
            no_user+=1

    if(no_rides==0 or no_user==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        creator = mongo.db.rides.find({"created_by":username})
        creator_rides=[]
        rides = list(mongo.db.rides.find({"rideId":rideId}))
        for i in creator:
            creator_rides.append(i["rideId"])
        if(rideId in creator_rides):
            return Response(json.dumps({}), status=400, mimetype='application/json')
        elif(username in rides[0]["users"]):
            return Response(json.dumps({}), status=400, mimetype='application/json')
        else:
            data = {"method":"join","collection":"rides","rideId":rideId,"data":{"users":username}}
            requests.post('http://127.0.0.1:5000/api/v1/db/write',json =data)
            return Response(json.dumps({}), status=200, mimetype='application/json')



#API to delete existing ride
@app.route('/api/v1/rides/<int:rideId>',methods=['DELETE'])
def delete_ride(rideId):
    C.requests_count+=1
    no_rides = mongo.db.rides.find({"rideId":rideId}).count()
    if(no_rides==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data = {"method":"delete","collection":"rides","data":{"rideId":rideId}}
        requests.post('http://127.0.0.1:5000/api/v1/db/write',json =data)
        return Response(json.dumps({}), status=200, mimetype='application/json')


#API for all database writes
@app.route('/api/v1/db/write',methods=["POST"])
def write():
    d_values = request.get_json()
    #d_values = json.loads(values)
    collection = d_values["collection"]
    data = d_values["data"]
    method = d_values["method"]
    # if(method=="put" and collection=="users"):
    #     mongo.db.users.insert(data)
    # if(method=="delete" and collection=="users"):
    #     mongo.db.users.remove(data)
    if(method=="post" and collection=="rides"):
        mongo.db.rides.insert(data)
    if(method=="join" and collection=="rides"):
        rideId = d_values["rideId"]
        mongo.db.rides.update({"rideId":rideId},{'$push':data})
    if(method=="delete" and collection=="rides"):
        mongo.db.rides.remove(data)
    return "done"


#API for all database reads
@app.route('/api/v1/db/read',methods=["POST"])
def read():
    d_values = request.get_json()
    #d_values = json.loads(values)
    collection = d_values["collection"]
    data = d_values["data"]
    method = d_values["method"]
    if(method=="get_all" and collection=="rides"):
        #result = dumps(mongo.db.rides.find(data,{"rideId":1,"created_by":1,"timestamp":1,"_id":0}))
        result=[]
        cursor = list(mongo.db.rides.find(data,{"rideId":1,"created_by":1,"timestamp":1,"_id":0}))
        for i in cursor:
            timestamp = i['timestamp'].split(':')
            date = timestamp[0].split('-')
            time = timestamp[1].split('-')
            current_time = datetime.now()
            record_time = datetime(int(date[2]),int(date[1]),int(date[0]),int(time[2]),int(time[1]),int(time[0]))
            #print(record_time)
            #print(current_time)
            if(record_time>=current_time):
                result.append(i)
        result = dumps(result)

    if(method=="get_ride" and collection=="rides"):
        result = dumps(mongo.db.rides.find(data,{"_id":0}))

    return(result)


#API to clear db
@app.route('/api/v1/db/clear',methods=["POST"])
def clear():
    #global requests_count
    #requests_count+=1
    mongo.db.rides.remove({})
    return '{}'

#API to count http requests to rides app
@app.route('/api/v1/_count',methods=["GET"])
def getrequestcount():
    return '[ '+str(C.requests_count)+' ]'

#reset requests count for rides app
@app.route('/api/v1/_count',methods=["DELETE"])
def resetrequestcount():
    C.requests_count=0
    return '{}'

#API to get total number of rides
@app.route('/api/v1/rides/count',methods=["GET"])
def getnorides():
    C.requests_count+=1
    result = mongo.db.rides.find().count()
    if(result==0):
        return Response('[ '+str(result)+' ]', status=204, mimetype='application/json')
    else:
        return('[ '+str(result)+' ]')

#@app.errorhandler(404)
#def not_found(e):
#    global requests_count
#    requests_count+=1
#    return Response('',status=404)

@app.errorhandler(400)
def not_found_bad(e):
    C.requests_count+=1
    return Response('',status=400)

@app.errorhandler(405)
def not_method(e):
    C.requests_count+=1
    return Response('',status=405)

if __name__ == '__main__':
        app.debug=True
        app.run(host='0.0.0.0')