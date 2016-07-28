"""Cloud Foundry test"""
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import os
import requests
import json
from collections import defaultdict
import random
import networkx as nx
import re
from math import *
import time
#import MySQLdb
#import config
import pymysql
import pystache
import math


connection = pymysql.connect(host='us-cdbr-iron-east-04.cleardb.net',
                             user='bbc1aa73c9c33a',
                             password='6b864e65',
                             db='ad_01dfa487e753bc4',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
with open ("search.mustache", "r") as myfile:
    data=myfile.readlines()

''.join(data)
mustacheSearchFile =''.join(data)# 'Hi {{#Array}}<p>{{name}}{{email}} can help you with  {{#willgive}}{{name}}{{/willgive}}</p>{{/Array}}!'
print mustacheSearchFile

users = '''
{"users":[{"id":1,
            "name":"Lucien",
            "email":"lchrist@us.ibm.com",
            "have":[
                    {"php":"6"},
                    {"python":"10"},
                    {"java":"4"},
                    {"sql":"2"},
                    {"ajax":"5"},
                    {"twitter API":"8"},
                    {"REST API":"5"},
                    {"Machine Learning":"20"}
                    ],
            "need":[
                    {"CORS":"1"},
                    {"ibm bluemix":"1"},
                    {"node.js":"1"}
                   ],
            "willgive":[],
            "willneed":[]

            },

            {"id":2,
            "name":"Rohit",
            "email":"rkutty@us.ibm.com",
            "have":[{"php":"10"},
                        {"data mining":"7"},
                        {"ibm bluemix":"5"},
                        {"sql":"10"},
                        {"text mining":"5"},
                        {"data analysis":"10"},
                        {"analytics":"10"},
                        {"R":"5"}],
            "need":[{"design patterns":"1"},
                    {"machine learning":"1"},
                    {"twitter API":"1"}],
            "willgive":[],
            "willneed":[]

            }
            ,
            {"id":3,
            "name":"James",
            "email":"greeneja@us.ibm.com",
            "have":[{"php":"10"},
                        {"java":"10"},
                        {"ibm bluemix":"5"},
                        {"sql":"10"},
                        {"javascript":"5"},
                        {"data mining":"5"},
                        {"scala":"10"},
                        {"twilio":"5"}],
            "need":[{"security":"1"},
                    {"encryption":"1"},
                    {"javascript":"1"}],
            "willgive":[],
            "willneed":[]
                    

            }
        ]
}

'''

app = Flask(__name__)
CORS(app)

# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

@app.route('/')
def hello_world():
    return 'Hello World! I am running on port ' + str(port)

'''
@app.route('/closedb')
def hello_world():
    connection.close()
    return "closed db"
'''
@app.route('/analyze',methods=['GET','POST'])
def analyze():

    searchJson = request.args.get('search')
    
    
    actualJson = json.loads(searchJson)
    
    #print actualJson["array"]
    #print "USERNAME: ",actualJson["username"]

    username = actualJson["username"]

    searchterms = actualJson["array"]



    ##Get JSON from database.
    usersJson = json.loads(users)
    #print usersJson["users"][0]
    
    usersList = getDBJsonUsersList()

    '''
    usersList2 = []
    for user in usersJson["users"]:
        usersList.append(User(user))

    '''

    user = User(getDBJsonUser(username))

    usersList = sorted(usersList, key=lambda x: user.searchSimilarity(x,searchterms,add=True), reverse=True)



    prejsonlist = []
    
    for user in usersList:
        similarity = user.searchSimilarity(user,searchterms,add=False)
        #print similarity,user
        if(user.searchSimilarity(user,searchterms,add=False)>0):
            prejsonlist.append(user.json)
    #print "LEN",len(prejsonlist)
    return renderJSON(json.loads('{"Array":'+json.dumps(prejsonlist)+'}'))
    #pystache.render('Hi {{person}}!', {'person': 'Mom'})
    #return json.dumps(prejsonlist)
    

    ##Return JSON data

##Calling flask on

def getDBJsonUser(username):


    result = {}

    
    # Read a single record
    sql = "SELECT id, username,firstname,lastname,position,location FROM users WHERE username = '"+username+"';"
    #print sql
    cursor.execute(sql)
    result = cursor.fetchone()
            

    print(result)
    json = {"id":result['id'],
            "username":result['username'],
            "firstname":result['firstname'],
            "lastname":result['lastname'],
            "position":result['position'],
            "location":result['location'],
            "have":[],
            "need":[],
            "willgive":[],
            "willneed":[]}

    sql = "SELECT skill, recommendations FROM userskills WHERE userid = '"+str(result['id'])+"';"

    cursor.execute(sql)
    
    for row in cursor.fetchall():

        json['have'].append({row['skill']:row['recommendations']})

    sql = "SELECT skill FROM userneeds WHERE userid = '"+str(result['id'])+"';"

    cursor.execute(sql)
    
    for row in cursor.fetchall():

        json['need'].append({row['skill']:1})

    #print "JSON GETDBJSONUSER::::",json
    
    return json
    

def getDBJsonUsersList():


    result = {}

 
    # Read a single record
    sql = "SELECT id, username FROM users;"

    cursor.execute(sql)
    usersList = []
    for row in cursor.fetchall():

        usersList.append(User(getDBJsonUser(row['username'])))
        
    #print usersList
    return usersList


    
def renderJSON(json):
    #json = '{"Array":'+json+'}'
    print json
    html = pystache.render(mustacheSearchFile, json)
    print html
    return html

def jaccard_similarity(x,y):

    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)

#print jaccard_similarity([0,1,2,5,6],[0,2,3,5,7,9])



class User:
    def __init__(self,json):
        self.json = json

    def searchSimilarity(self,user,searchterms,add):
        #print "-------",user.json

        summation = 0
        total = 0
        #print user
        skills = user.json["have"]
        #print skills
        for item in skills:
            for element in searchterms:
                #print item,element
                #print item.items()
                
                if item.items()[0][0] == element.items()[0][0]:
                    summation+=float(item.items()[0][1])*float(element.items()[0][1])
                    if(add):
                        user.json["willgive"].append({"id":user.json["id"],"location":user.json["location"],"position":user.json["position"],"username":user.json["username"],"firstname":user.json["firstname"],"lastname":user.json["lastname"],"name":item.items()[0][0],"score":item.items()[0][1]})
                total += float(item.items()[0][1])

        total2 = 0
        summation2 = 0
        if(summation > 0):
            skills = user.json["need"]
            #print skills
            for item in skills:
                for element in self.json["have"]:
                    #print item,element
                    
                    
                    if item.items()[0][0] == element.items()[0][0]:
                        summation2+=float(item.items()[0][1])*float(element.items()[0][1])
                        if(add):
                            user.json["willneed"].append({"id":user.json["id"],"location":user.json["location"],"position":user.json["position"],"username":user.json["username"],"firstname":user.json["firstname"],"lastname":user.json["lastname"],"name":item.items()[0][0],"score":element.items()[0][1]})
                    total2 += float(element.items()[0][1])
    #["willgive"][item.items()[0][0]] = "1"
        else:
            return 0.0
        #print summation
        #print total
        if(total == 0.0):
            return 0.0
        #print "SCORE OF SIMILARITY:",float(summation)/float(total)
        
        return float(summation+(summation2/total2))
        
    def searchJSON(self,user,searchterms):
        #
        print user


if __name__ == '__main__':
    #analyzeTweets('yahoo',10000,"")
    app.run(host='0.0.0.0', port=port)


