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

#API to create new ride
@app.route('/api/v1/rides',methods=['POST'])
def add_ride():
    if(not request.json):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    data = request.get_json()
    username = request.get_json()["created_by"]
    #no_user = mongo.db.users.find({"username":username}).count()
    #print(username)
    header = {'Origin':'34.196.181.165'}
    users = requests.get('http://test-project-80298398.us-east-1.elb.amazonaws.com/api/v1/users')
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
            #no_rides = mongo.db.rides.count()
            no_res = requests.get('http://127.0.0.1:5000/api/v1/rides/count')
            if(no_res.status_code==204):
                rideId = 1
            else:    
                no_rides = json.loads(no_res.content)[0]
                allrides_res = requests.get('http://127.0.0.1:5000/api/v1/rides/allrides')
                allrides = json.loads(allrides_res.content.decode("utf-8"))
                rideId = list(allrides)[no_rides-1]["rideId"]+1
            data= {"method":"post","collection":"rides","data":{"rideId":rideId,"created_by":username,"users":[],"timestamp":timestamp,"source":source,"destination":destination}}
            requests.post('http://52.3.57.80/api/v1/db/write',json =data)
            return Response(json.dumps({}), status=201, mimetype='application/json')
        else:
            return Response(json.dumps({}), status=400, mimetype='application/json')



#API to get rides given source and destination as query params
@app.route('/api/v1/rides',methods=['GET'])
def list_rides():
    source = request.args.get("source")
    destination = request.args.get("destination")
    with open("AreaNameEnum.csv") as f:
        lines = sum(1 for line in f)
    #print(lines)
    if(int(source) in range(1,lines) and int(destination) in range(1,lines) and int(source)!=int(destination)):
        data = {"method":"get_all","collection":"rides","data":{"source":int(source),"destination":int(destination)}}
        response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
        if(json.loads(response.content.decode("utf-8"))==[]):
            return Response(json.dumps({}), status=204, mimetype='application/json')
        else:
            return(response.content)
    else:
        return Response(json.dumps({}), status=400, mimetype='application/json')



#API to get ride details given rideID in url
@app.route('/api/v1/rides/<int:rideId>',methods=['GET'])
def ride_details(rideId):  
    #no_rides = mongo.db.rides.find({"rideId":rideId}).count()
    no_res = requests.get('http://127.0.0.1:5000/api/v1/rides/rideIdcount/'+str(rideId))
    no_rides = json.loads(no_res.content.decode("utf-8"))[0]
    if(no_rides==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data = {"method":"get_ride","collection":"rides","data":{"rideId":rideId}}
        response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
        return(response.content)



#API to add user to existing ride (join the ride)
@app.route('/api/v1/rides/<int:rideId>',methods=['POST'])
def join_ride(rideId):
    #no_rides = mongo.db.rides.find({"rideId":rideId}).count()
    no_res = requests.get('http://127.0.0.1:5000/api/v1/rides/rideIdcount/'+str(rideId))
    no_rides = 0
    if(no_res.status_code!=204):
        no_rides = json.loads(no_res.content)[0]
    data = request.get_json()
    username = request.get_json()["username"]
    #no_user = mongo.db.users.find({"username":username}).count()
    header = {'Origin':'34.196.181.165'}
    users = requests.get('http://test-project-80298398.us-east-1.elb.amazonaws.com/api/v1/users')
    users_list = json.loads(users.content.decode("utf-8"))
    no_user=0
    for record in users_list:
        if(record['username']==username):
            no_user+=1

    if(no_rides==0 or no_user==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        #creator = mongo.db.rides.find({"created_by":username})
        creator_res = requests.get('http://127.0.0.1:5000/api/v1/rides/userrides/'+username)
        creator = json.loads(creator_res.content.decode("utf-8"))
        creator_rides=[]
        #rides = list(mongo.db.rides.find({"rideId":rideId}))
        rides_res = requests.get('http://127.0.0.1:5000/api/v1/rides/rideIdrides/'+str(rideId))
        rides = list(json.loads(rides_res.content.decode("utf-8")))
        for i in creator:
            creator_rides.append(i["rideId"])
        if(rideId in creator_rides):
            return Response(json.dumps({}), status=400, mimetype='application/json')
        elif(username in rides[0]["users"]):
            return Response(json.dumps({}), status=400, mimetype='application/json')
        else:
            data = {"method":"join","collection":"rides","rideId":rideId,"data":{"users":username}}
            requests.post('http://52.3.57.80/api/v1/db/write',json =data)
            return Response(json.dumps({}), status=200, mimetype='application/json')



#API to delete existing ride
@app.route('/api/v1/rides/<int:rideId>',methods=['DELETE'])
def delete_ride(rideId):
    #no_rides = mongo.db.rides.find({"rideId":rideId}).count()
    no_res = requests.get('http://127.0.0.1:5000/api/v1/db/rides/count')
    if(no_res.status_code==204):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data = {"method":"delete","collection":"rides","data":{"rideId":rideId}}
        requests.post('http://52.3.57.80/api/v1/db/write',json =data)
        return Response(json.dumps({}), status=200, mimetype='application/json')


#API to clear db
@app.route('/api/v1/db/clear',methods=["POST"])
def clear():
    data = {"method":"clear","collection":"rides","data":"null"}
    requests.post('http://52.3.57.80/api/v1/db/write',json =data)
    return '{}'



#API to get total number of rides
@app.route('/api/v1/rides/count',methods=["GET"])
def getnorides():    
    data = {"method":"get_rides_count","collection":"rides","data":"null"}
    response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
    ctr = int(response.content)
    if(ctr==0):
        return Response('[ '+str(ctr)+' ]', status=204, mimetype='application/json')
    else:
        return('[ '+str(ctr)+' ]')


#API to get rides based on username
@app.route('/api/v1/rides/userrides/<username>',methods=["GET"])
def get_user_rides(username):    
    data = {"method":"get_user_rides","collection":"rides","data":{"created_by":username}}
    response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
    return Response(response.content, status=200, mimetype='application/json')



#API to get rides based on rideId
@app.route('/api/v1/rides/rideIdrides/<int:rideId>',methods=["GET"])
def get_id_rides(rideId):    
    data = {"method":"get_id_rides","collection":"rides","data":{"rideId":rideId}}
    response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
    return Response(response.content, status=200, mimetype='application/json')


#API to get all rides 
@app.route('/api/v1/rides/allrides',methods=["GET"])
def get_all_rides():    
    data = {"method":"get_all_rides","collection":"rides","data":"null"}
    response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
    return Response(response.content, status=200, mimetype='application/json')


#API to get number of rides based on rideId
@app.route('/api/v1/rides/rideIdcount/<int:rideId>',methods=["GET"])
def get_no_id_rides(rideId):    
    data = {"method":"get_id_rides_count","collection":"rides","data":{"rideId":rideId}}
    response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
    ctr = int(response.content)
    if(ctr==0):
        return Response('[ '+str(ctr)+' ]', status=204, mimetype='application/json')
    else:
        return('[ '+str(ctr)+' ]')


if __name__ == '__main__':	
	app.debug=True
	app.run(host="0.0.0.0")
