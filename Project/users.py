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

#API to add user
@app.route('/api/v1/users',methods=['PUT'])
def add_user():
    username = request.get_json()["username"]
    password = request.get_json()["password"]
    #print(username)
    #print(password)
    #no_user = mongo.db.users.find({"username":username}).count()
    allusers_res = requests.get('http://127.0.0.1:5000/api/v1/users')
    #print(allusers_res.content)
    no_user=0
    if(allusers_res.status_code!=204):
        allusers = json.loads(allusers_res.content.decode("utf-8"))
        for i in list(allusers):
            if(i["username"]==username):
                no_user = 1
    if(no_user==0):
        if(re.match("^[a-fA-F0-9]{40}$",password)):
            data ={"method":"put","collection":"users","data":{"username":username,"password":password}}
            requests.post('http://52.3.57.80/api/v1/db/write',json =data)
            return Response(json.dumps({}),status=201,mimetype='application/json')
        else:
            return Response(json.dumps({}), status=400,mimetype='application/json')
    else:
        return Response(json.dumps({}), status=400,mimetype='application/json')


#API to delete user
@app.route('/api/v1/users/<string:name>',methods=['DELETE'])
def delete_user(name):
    #no_user = mongo.db.users.find({"username":name}).count()
    allusers_res = requests.get('http://127.0.0.1:5000/api/v1/users')
    no_user=0
    if(allusers_res.status_code!=204):
        allusers = json.loads(allusers_res.content.decode("utf-8"))
        for i in list(allusers):
            if(i["username"]==name):
                no_user = 1
    if(no_user==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data ={"method":"delete","collection":"users","data":{"username":name}}
        requests.post('http://52.3.57.80/api/v1/db/write',json =data)
        return Response(json.dumps({}), status=200, mimetype='application/json')


#API to list users
@app.route('/api/v1/users',methods=['GET'])
def list_users():
    #print(result)
    data = {"method":"get_all","collection":"users","data":"null"}
    response = requests.post('http://52.3.57.80/api/v1/db/read',json =data)
    if(json.loads(response.content.decode("utf-8"))==[]):
        return Response(json.dumps({}), status=204, mimetype='application/json')
    else:
        return(response.content)


#API to clear db
@app.route('/api/v1/db/clear',methods=["POST"])
def clear():
    data = {"method":"clear","collection":"users","data":"null"}
    requests.post('http://52.3.57.80/api/v1/db/write',json =data)
    return '{}'



if __name__ == '__main__':	
	app.debug=True
	app.run(host='0.0.0.0')
