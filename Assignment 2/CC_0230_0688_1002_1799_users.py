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
app.config["MONGO_URI"] = "mongodb://users-mongo:27017/users"
mongo = PyMongo(app)
requests_count=0

#API to add user
@app.route('/api/v1/users',methods=['PUT'])
def add_user():
    global requests_count
    requests_count+=1
    username = request.get_json()["username"]
    password = request.get_json()["password"]
    #print(username)
    #print(password)
    no_user = mongo.db.users.find({"username":username}).count()
    if(no_user==0):
        if(re.match("^[a-fA-F0-9]{40}$",password)):
            data ={"method":"put","collection":"users","data":{"username":username,"password":password}}
            requests.post('http://127.0.0.1:5000/api/v1/db/users/write',json =data)
            return Response(json.dumps({}),status=201,mimetype='application/json')
        else:
            return Response(json.dumps({}), status=400,mimetype='application/json')
    else:
        return Response(json.dumps({}), status=400,mimetype='application/json')

#API to delete user
@app.route('/api/v1/users/<string:name>',methods=['DELETE'])
def delete_user(name):
    global requests_count
    requests_count+=1
    no_user = mongo.db.users.find({"username":name}).count()
    if(no_user==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data ={"method":"delete","collection":"users","data":{"username":name}}
        requests.post('http://127.0.0.1:5000/api/v1/db/users/write',json =data)
        return Response(json.dumps({}), status=200, mimetype='application/json')

#API to list users
@app.route('/api/v1/users',methods=['GET'])
def list_users():
    global requests_count
    requests_count+=1
    result = dumps(mongo.db.users.find({},{"_id":0}))
    #print(result)
    if(json.loads(result)==[]):
        return Response(json.dumps({}), status=204, mimetype='application/json')
    else:
        return(result)

#API to write to db
@app.route('/api/v1/db/users/write',methods=["POST"])
def write():
    d_values = request.get_json()
    #d_values = json.loads(values)
    collection = d_values["collection"]
    data = d_values["data"]
    method = d_values["method"]
    if(method=="put" and collection=="users"):
        mongo.db.users.insert(data)
    if(method=="delete" and collection=="users"):
        mongo.db.users.remove(data)

    return "done"




#API to clear db
@app.route('/api/v1/db/clear',methods=["POST"])
def clear():
    #global requests_count
    #requests_count+=1
    mongo.db.users.remove({})
    return '{}'

#API to count http requests to users app
@app.route('/api/v1/_count',methods=["GET"])
def getrequestcount():
    return '[ '+str(requests_count)+' ]'

#reset requests count for users app
@app.route('/api/v1/_count',methods=["DELETE"])
def resetrequestcount():
    global requests_count
    requests_count=0
    return '{}'

#@app.errorhandler(404)
#def not_found(e):
#    global requests_count
#    requests_count+=1
#    return Response('',status=404)

@app.errorhandler(400)
def not_found_bad(e):
    global requests_count
    requests_count+=1
    return Response('',status=400)

@app.errorhandler(405)
def not_method(e):
    global requests_count
    requests_count+=1
    return Response('',status=405)

if __name__ == '__main__':
        app.debug=True
        app.run(host='0.0.0.0')