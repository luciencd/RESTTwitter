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
<<<<<<< HEAD

import nltk
import time
#NLTK_DATA = '/Users/lucienchristie-dervaux/documents/RESTTwitter'
nltk.data.path.append('/Users/lucienchristie-dervaux/documents/RESTTwitter/nltk_data')
nltk.data.path.append('/home/vcap/app/nltk_data')
nltk.data.path = nltk.data.path[1:]

from nltk.corpus import stopwords
print nltk.data.path

c = {}
def getCache(url):
    
    try:
        return c[url]
    except TypeError:
        return False
    
def cached(url):
    #Obviously if its been 1 day, remove cache values
    
    if url in c:
        return True
    else:
        return False

    
def cache(url,data):
    c[url] = data
=======
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
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

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
<<<<<<< HEAD
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #print dir_path
    #return dir_path
    #print nltk.data.path
    keyword = str(request.args.get('keyword'))
    numTweets = int(request.args.get('numTweets'))
    numBubbles = int(request.args.get('numBubbles'))
    mainBool = str(request.args.get('main'))
    t = time.strftime("%B/%d")
    ##add date rounded to nearest hour to url, so that every hour, the thing gets updated
    
    url = t+keyword+str(numTweets)+str(numBubbles)+mainBool
    print url
    #cacheing


    #May need to add a hashtag to the token to make search more specific
    if(cached(url)):
        print "CACHED"
        return getCache(url)
    else:
        print "NOTCACHED"
        data = analyzeTweets(keyword,numTweets,request)
        cache(url,data)
        return data

##Calling flask on




class Node:
    def __init__(self,name,group,mass):
        self.name = name
        self.group = group
        self.mass = mass
        self.neighbors = {}
        self.value = 0

        self.valid = True

        ##list of tweets.
        self.count = 0
        self.happiness = 0.0
        self.anger = 0.0

        self.dupes = 0.0
        self.uniques = 0.0
    def addEdge(self,name,edge):
         
        if(name in self.neighbors):
            #print "duplicate"
            self.dupes+=1
        else:
            self.uniques+=1
        
        self.neighbors[name] = edge

    def existsNeighbor(self,neighbor):
        return neighbor in self.neighbors
=======

    searchJson = request.args.get('search')
    
    
    actualJson = json.loads(searchJson)
    
    #print actualJson["array"]
    #print "USERNAME: ",actualJson["username"]
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

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

<<<<<<< HEAD
        ##breadth first-search.
        if(graph.size <=0):
            return False
            
        
        index = 0
=======
##Calling flask on
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

def getDBJsonUser(username):


    result = {}

    
    # Read a single record
    sql = "SELECT id, username,firstname,lastname,position,location FROM users WHERE username = '"+username+"';"
    #print sql
    cursor.execute(sql)
    result = cursor.fetchone()
            
<<<<<<< HEAD
            groups.append((group,visited,num))

        #print groups
        groups = sorted(groups,key=lambda group:-group[2])
        #for item in groups:
        #    print item
        #gets biggest group of nodes
        visited = groups[0][1]
        #print len(visited)
        
        for name,node in graph.nodes.items():
            #print node
            if name not in visited:
                #print name,len(node.neighbors)
                node.valid = False
                for key,value in node.neighbors.iteritems():
                    value.valid = False

    
    def filteredges(self,graph):
        for name,node in graph.nodes.items():
            neighbor_array = node.neighbors.values()
            for edge in neighbor_array:
                edge.valid = False
            
        for name,node in graph.nodes.items():

            neighbor_array = node.neighbors.values()
            
            neighbor_array = sorted(neighbor_array,key=lambda edge:edge.weight,reverse=False)
            index = 0
            
            for edge in neighbor_array:
                if(index <= 15):
                    edge.valid = True

                index +=1


    #dynamic programming filter.                    
    def filterit(self,graph,func):
        #print "invalidating"
 
        for node in graph.nodes:
            if(func(node)):
                node.valid = False
                for key,value in node.neighbors.iteritems():
                    value.valid = False

                
class twitter:

    def __init__(self,keyword,numTweets):
        ##Must make ths thing link to envir vars from bluemix
        self.TWITTER_USERNAME = "f8499318-83de-4e36-bb68-adf3cd8ab000"
        self.TWITTER_PASSWORD = "RdCd9hrTag"
        self.NO_OF_TWEETS_TO_RETRIEVE = numTweets
        self.keyword = keyword
        #self.min_cutoff = self.NO_OF_TWEETS_TO_RETRIEVE/300
        self.amount_shown = 100
        self.percent = 1.0
        self.twe = {}
        self.sentiments = {}
        self.output = {}
        self.graph = Graph()
        self.size = -1

        
        self.df = {}
        
    def reduceit(self,string):
        #print string
        if(len(string) < 2):
            return ""
        string = string[0]+re.sub(r'\W', '', string[1:])
        #print string
        return string

    def addToGraph(self,sentiment,tokens):

        '''
        #body = re.sub(':,;%.\n',' ',body)
        #body = re.sub('',' ',body)
        body = body.lower()
        hashtags = body.split(' ')
        handle = body.split(' ')
        #print handle
        
        hashtags = map(lambda x: self.reduceit(x),hashtags)
        handle = map(lambda x: self.reduceit(x),handle)

        for i in range(len(hashtags)):
            tokens = ''.join(e for e in string if e.isalnum())
            

        hashtags = filter(lambda x:( x != ""),hashtags)
        handle = filter(lambda x:( x != ""),handle)

#        hashtags = filter(lambda x:(x!=str("#"+self.keyword)),hashtags)
#        handle = filter(lambda x:(x!=str("@"+self.keyword)),handle)

        hashtags = filter(lambda x:( x != "#"),hashtags)
        handle = filter(lambda x:( x != "@"),handle)


        hashtags = filter(lambda x:( x[0] == "#"),hashtags)
        handle = filter(lambda x:( x[0] == "@"),handle)

        print handle
        '''



        #print "tweet:",body
        #print "content: ",hashtags+handle
        #print "handle:",handle
        for item in tokens:
            ##Add or edit the node itself
            oldnode = ""
            if(self.graph.nodeExists(item)):
                oldnode = self.graph.getNode(item)

            else:
                node = Node(item,0,1)
                '''
                if(item[0] == '#'):
                    node = Node(item,0,len(hashtags)+len(handle))
                else:
                    node = Node(item,1,len(hashtags)+len(handle))
                '''

                self.graph.addNode(node)
                oldnode = self.graph.getNode(item)

            oldnode.mass += 1
            if(sentiment == 0):
                oldnode.anger+=1
            elif(sentiment == 1):
                oldnode.happiness+=1

            oldnode.count += 1
            #print self.graph.getNode(item)




            #nx.set_node_attributes(G, 'mass', {1:3.5, 2:56})


        for node1 in tokens:
            for node2 in tokens:
                #
                edge = ""
                if(self.graph.edgeExists(node1,node2)):
                    #print "editing link between (x,y)",node1,node2
                    edge = self.graph.getEdge(node1,node2)

                else:
                    self.graph.addEdge(node1,node2)
                    edge = self.graph.getEdge(node1,node2)

                    #print "putting link between (x,y)",node1,node2

                edge.weight += 1#1.0/(float)(len(tokens))
                if(sentiment == 0):
                    edge.anger+=1
                elif(sentiment == 1):
                    edge.happiness+=1

                edge.count += 1


    def fetchTweets(self, term):
          payload = {"q": term, "size": self.NO_OF_TWEETS_TO_RETRIEVE}
          response = requests.get("https://cdeservice.mybluemix.net:443/api/v1/messages/search", params=payload, auth=(self.TWITTER_USERNAME, self.TWITTER_PASSWORD))
          
          twe = json.loads(response.text)
          #print len(twe['tweets'])
          self.twe = twe['tweets']
          return twe

    def getSentiment(self):
        ##ideally compile all words here to begin with to get idf score
        
        for i in range(self.NO_OF_TWEETS_TO_RETRIEVE):
            sentiment = "AMBIVALENT"
            body = ""
            symbols = []
            try:
                sentiment = self.twe[i]['cde']['content']['sentiment']['polarity']

            except KeyError:
                pass
            except IndexError:
                pass
            try:

                body = self.twe[i]['message']['body']
                symbols = self.twe[i]['message']['twitter_entities']['symbols']
                ##Need tool that can extract key words from string sentence.
            except KeyError:
                pass
            except IndexError:
                pass

            if(sentiment == "POSITIVE"):
                sentint = 1
                #print "pos"
            elif(sentiment == "NEGATIVE"):
                sentint = 0
                #print "neg"
            else:
                sentint = 0.5
            ##for this tweet,


            tokens = self.tokenize(body)
            
 
            
            scores = self.scoreize(tokens)
            
            
            self.addToGraph(sentint, scores)
            
    def collectText(self):

        listOfWords = []
        
        for i in range(self.NO_OF_TWEETS_TO_RETRIEVE):
            body = ""

            try:

                body = self.twe[i]['message']['body']
                symbols = self.twe[i]['message']['twitter_entities']['symbols']
                ##Need tool that can extract key words from string sentence.
            except KeyError:
                pass
            except IndexError:
                pass




            tokens = self.tokenize(body)

            

            uniques = set(tokens)
            
            for word in uniques:
                if word in self.df:
                    self.df[word]+= 1
                else:
                    self.df[word] = 1


        
    def tokenize(self,body):
        
        #print body
        ##map single string body to sentence
        sentences = nltk.tokenize.sent_tokenize(body)
        #print sentences

        ##map each sentence to single word tokens.
        tokens = [nltk.tokenize.word_tokenize(s) for s in sentences]
        #print tokens

        

 
        ##keep only top 4 words with highest tdidf score in all sentences,
        ##where each sentence is a separate document(or not for now)
        listoftokens = []
        for sentence in tokens:

            for token in sentence:
                ##time to normalize every token
                
                normalizedToken = token.lower()
                
                listoftokens.append(normalizedToken)

        
        return listoftokens

    def scoreize(self,tokens):
        ## [("word","score")] ordered by score



        scores = []
        #print "scoreize"
        #print tokens,"\n\n"
        
        tokens = [token for token in tokens if token not in stopwords.words('english')]
        tokens = [token for token in tokens if len(token)>3]
        tokens = [token for token in tokens if token not in ["http","https"]]
        #print tokens,"\n\n"

        for token in set(tokens):
            ##count how many times token appears in this list tokens
            tf = tokens.count(token)

            ##get the inverse of the frequency of how much this token appears in all documents
            df = self.df[token]
            if(df < 2):
                continue
            
            idf = 1.0/df;
     
                
            scores.append( (token,round(tf,5),round(df,5),round(idf,5),round(tf*idf,5) ))
            #print scores[len(scores)-1],tokens,"\n\n"
        scores = sorted(scores, key=lambda tup: tup[3],reverse=True)

        newlist = []
        for score in scores[0:min(4,len(scores))]:
            newlist.append(score[0])

        #print scores[0:4]
        
        #for tokens in scores[0:2]:
        #   print tokens[0],tokens[1],tokens[2],tokens[3]
        return newlist
                    #print token,"appeared ", df,"times total. appeared ",tf," times in the document giving a score of:",tf*idf
        
            

    

        
    def printGraph(self,search):

        edges = list(self.graph.edges(data=True))
        for item in edges:
            print item


    def returnJSON(self):
        #edges = list(self.graph.edges(data=True))

        #nodes = self.graph.edges(data=True)
        jsonObj = {}
        nodesjsonlist = []
        for node in self.graph.outputNodes():

            #print {'name':item}
=======

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
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

        json['have'].append({row['skill']:row['recommendations']})

<<<<<<< HEAD
            #print '{"name":',node.name,',"group":',node.group,',"mass":',node.mass,',"value":',node.value#node.neighbors#,node.value
            nodejson = {'name':node.name,'group':node.group,'mass':len(node.neighbors),'sentiment':node.getSentiment()}
=======
    sql = "SELECT skill FROM userneeds WHERE userid = '"+str(result['id'])+"';"
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

    cursor.execute(sql)
    
    for row in cursor.fetchall():

        json['need'].append({row['skill']:1})

    #print "JSON GETDBJSONUSER::::",json
    
    return json
    

<<<<<<< HEAD
            #print {'source':edge.source.value,'target':edge.target.value,'weight':edge.weight}
            edgejson = {'source':edge.source.value,'target':edge.target.value,'value':edge.weight,'sentiment':edge.getSentiment()}
            edgesjsonlist.append(edgejson)
=======
def getDBJsonUsersList():
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9


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

<<<<<<< HEAD
    ##put all tweets in list.
    tweets.fetchTweets(keyword)
    print "fetchtweets"

    ##create text collection
    tweets.collectText()
    print "collecttext"
    ##get all the sentiment for nodes and generate graph.
    tweets.getSentiment()
    print "getSentiment"

    
    
    ##reset all nodes to unfiltered unvisited.
    tweets.graph.reset(tweets.graph)
    print "reset"
    print len(tweets.graph.nodes)


    
    ##only allowing 5 top edges per node.
    tweets.graph.filteredges(tweets.graph)

    
    ##filtering things based on get requests
    if(mainBool == "True"):
        ##filter out all the nodes that are not a part of the biggest connected graph
        tweets.graph.filtermain(tweets.graph)
    
    print "filtering"
=======
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)

#print jaccard_similarity([0,1,2,5,6],[0,2,3,5,7,9])


>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

class User:
    def __init__(self,json):
        self.json = json

<<<<<<< HEAD
    print "numbering bubbles"
    ##filter only leaving top n nodes.
    #tweets.graph.invalidate(tweets)

    
    
    tweets.graph.renameOrdered()
    jsondata = tweets.returnJSON()
    #print len(jsondata)

    #returning json data of the graph.
    print "finished"
    return json.dumps(jsondata)
=======
    def searchSimilarity(self,user,searchterms,add):
        #print "-------",user.json
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9

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
<<<<<<< HEAD
    #analyzeTweets('yahoo',50,"")
    
=======
    #analyzeTweets('yahoo',10000,"")
>>>>>>> ba66a2fc79ad5eb26a68d4c81742c122ee8396a9
    app.run(host='0.0.0.0', port=port)


