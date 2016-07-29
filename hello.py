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

import nltk

import time

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

    
app = Flask(__name__)
CORS(app)

# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

@app.route('/')
def hello_world():
    return 'Hello World! I am running on port ' + str(port)

@app.route('/analyze',methods=['GET','POST'])
def analyze():

    keyword = str(request.args.get('keyword'))
    numTweets = int(request.args.get('numTweets'))
    numBubbles = int(request.args.get('numBubbles'))
    mainBool = str(request.args.get('main'))
    t = time.strftime("%B/%d")
    ##add date rounded to nearest hour to url, so that every hour, the thing gets updated
    
    url = t+keyword+str(numTweets)+str(numBubbles)+mainBool
    print url
    #cacheing
    if(False):#cached(url)):
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

    def getNeighbor(self,neighbor):
        if(self.existsNeighbor(neighbor)):
            return self.neighbors[neighbor]

    def isValid(self):
        return self.valid


            
    def getSentiment(self):

        if(self.happiness+self.anger == 0):
            return 50
        else:
            return (int)(100.0*((self.happiness)/(self.happiness+self.anger)))

class Edge:
    def __init__(self,node1,node2):
        self.source = node1
        self.target = node2
        self.weight = 0

        self.valid = True
        self.visited = False

        self.count = 0
        self.happiness = 0.0
        self.anger = 0.0
    def getTargetValue(self):
        return self.target.value
    def getSourceValue(self):
        return self.source.value

    def setWeight(self,weight):
        self.weight=weight

    def getWeight(self):
        return self.weight

    def isValid(self):
        return self.valid

    def getSentiment(self):
        if(self.happiness+self.anger == 0):
            return 50
        else:
            return (int)(100.0*((self.happiness)/(self.happiness+self.anger)))


class Graph:
    def __init__(self):
        self.nodes = {}
        self.size = 0
        self.edges = {}
        self.count = 0
        self.happiness = 0
        self.anger = 0
    def addNode(self,node):
        self.nodes[node.name] = node
        self.size+=1

    def getNode(self,name):
        return self.nodes[name]

    def getAdjacentNodes(self,name):
        return self.nodes[name].neighbors

    def nodeExists(self,name):
        if(name in self.nodes):
            return True
        else:
            return False

    def edgeExists(self,name1,name2):
        if(self.nodeExists(name1) and self.nodeExists(name2)):
            if(self.getNode(name1).existsNeighbor(name2) and self.getNode(name2).existsNeighbor(name1)):
                return True

        return False

    def getEdge(self,name1,name2):
        if(self.edgeExists(name1,name2)):
            return self.getNode(name1).getNeighbor(name2)

    def addEdge(self,name1,name2):


        if(self.nodeExists(name1) and self.nodeExists(name2)):
            edge = Edge(self.getNode(name1),self.getNode(name2))
            self.getNode(name1).addEdge(name2,edge)
            self.getNode(name2).addEdge(name1,edge)
            self.edges[edge] = edge
            #self.edges[edge] = edge

    def renameOrdered(self):
        i=0
        for item,value in self.nodes.iteritems():
            if(value.isValid()):
                value.value = i
                i+=1

    #should probably cache
    def outputNodes(self):
        output = []
        for name, node in self.nodes.iteritems():

           if(node.isValid()):
               output.append(node)
        #print "nodes num",len(output)
        return output

    def outputEdges(self):
        output = []
        for key, value in self.edges.iteritems():
            if(value.isValid()):
               output.append(value)
        #print "edges num",len(output)
        return output

    ## make it so we only get top n nodes.
    ## make it a functional programming option.
    def invalidate(self,graph,number):
        #print "invalidating"
        #local_amount = (int)(len(self.nodes)*graph.percent)
        local_amount = number
        unordered_list = []
        for name,node in self.nodes.iteritems() :
            #node.valid = True
            if(node.valid):
                unordered_list.append(node)
            #print node.name,node.mass,len(node.neighbors)
            #for key,value in node.neighbors.iteritems():
                #print value.isValid()
                #value.valid = True

        unordered_list.sort(key=lambda node: -len(node.neighbors))
        #print "unorder"
        #print unordered_list[0:min(graph.amount_shown,len(unordered_list))]

        for node in unordered_list[min(local_amount,len(unordered_list)):len(unordered_list)]:
            #print node.name,node.mass,len(node.neighbors)
            node.valid = False

            for key,value in node.neighbors.iteritems():
                #print value.isValid()
                #print value.source.name,value.target.name
                value.valid = False



            #print ""

    ##clear all filters.
    def reset(self,graph):
        for name,node in self.nodes.iteritems():
            node.valid = True
            node.visited = True
            for key,value in node.neighbors.iteritems():
                value.valid = True
                

    def filtermain(self,graph):
        ##create map of groups of nodes, rank them by size, choose greatest,
        ##then remove everything else.

        ##breadth first-search.
        if(graph.size <=0):
            return False
            
        
        index = 0

        groups = 0
        maxnode = graph.nodes.items()[0][1]
        #
        for name,node in graph.nodes.items():
            #print node.neighbors
            node.visited = False
            if(len(node.neighbors) > len(maxnode.neighbors)):
                maxnode = node

        #print maxnode.dupes,maxnode.uniques

 
        #print maxnode.neighbors.items()
        group = -1
        groups = []
        while(index < len(graph.nodes)):
            #print "firstnode",graph.nodes.items()[index][1]
            if(graph.nodes.items()[index][1].visited == True):
                index+=1
                continue
            
            group+=1               
            visited = {}
            queue = [graph.nodes.items()[index][1]]
            num = 0
            while(len(queue) > 0):
                node = queue[0]
                #print node
                #print queue
                queue = queue[1:]
                #print queue
                node.visited = True
                visited[node.name] = node
                num+=1
                for name, neighbor in node.neighbors.items():
                    #print name
                    if(neighbor.target.visited == False):
                        queue.append(neighbor.target)

            
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
                node = Node(item,0,len(tokens))
                '''
                if(item[0] == '#'):
                    node = Node(item,0,len(hashtags)+len(handle))
                else:
                    node = Node(item,1,len(hashtags)+len(handle))
                '''

                self.graph.addNode(node)
                oldnode = self.graph.getNode(item)

            oldnode.mass += len(tokens)
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

                edge.weight += 1.0/(float)(len(tokens))
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
            
            self.addToGraph(sentint, tokens)
            
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
                ''.join(e for e in normalizedToken if e.isalnum())
                listoftokens.append(normalizedToken)

        
        return listoftokens

    def scoreize(self,tokens):
        ## [("word","score")] ordered by score

        scores = []
        for token in tokens:
            ##count how many times token appears in this list tokens
            tf = tokens.count(token)

            ##get the inverse of the frequency of how much this token appears in all documents
            df = self.df[token]
            idf = 1.0/df;
            
            scores.append( (token,round(tf,5),round(df,5),round(idf,5),round(tf*idf,5) ))

        scores = sorted(scores, key=lambda tup: -tup[3])
        print scores[0:4]
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


            #print '{"name":',node.name,',"group":',node.group,',"mass":',node.mass,',"value":',node.value#node.neighbors#,node.value
            nodejson = {'name':node.name,'group':node.group,'mass':len(node.neighbors),'sentiment':node.getSentiment()+random.randint(-7,7)}

            #print {'name':item.name,'group':item.group,'size':item.size}

            #print 'json','name',item['name'],'group',item['group'],'size',item['size']
            nodesjsonlist.append(nodejson)
        jsonObj['nodes'] = nodesjsonlist

        edgesjsonlist = []
        for edge in self.graph.outputEdges():

            #print {'source':edge.source.value,'target':edge.target.value,'weight':edge.weight}
            edgejson = {'source':edge.source.value,'target':edge.target.value,'value':edge.weight,'sentiment':edge.getSentiment()+random.randint(-7,7)}
            edgesjsonlist.append(edgejson)


            #if(self.existsNode(edge[1])):

        jsonObj['links'] = edgesjsonlist

        return jsonObj
#pass in filter function.
def analyzeTweets(keyword,numTweets,request):
    try: 
        numBubbles = int(request.args.get('numBubbles'))
    except AttributeError:
        numBubbles = 0

    try:
        mainBool = str(request.args.get('main'))
    except AttributeError:
        mainBool = "True"


    
    tweets = twitter(keyword,numTweets)
    ##dont bother with keyword and numTweets arguments.

    

    ##put all tweets in list.
    tweets.fetchTweets(keyword)

    ##create text collection
    tweets.collectText()
    
    ##get all the sentiment for nodes and generate graph.
    tweets.getSentiment()

    
    
    ##reset all nodes to unfiltered unvisited.
    tweets.graph.reset(tweets.graph)


    
    ##filtering things based on get requests
    if(mainBool == "True"):
        ##filter out all the nodes that are not a part of the biggest connected graph
        tweets.graph.filtermain(tweets.graph)

    ##getting number of top bubbles to display.
    if(numBubbles > 0):
        ##filter only leaving top n nodes.
        tweets.graph.invalidate(tweets,numBubbles)

    ##filter only leaving top n nodes.
    #tweets.graph.invalidate(tweets)

    
    
    tweets.graph.renameOrdered()
    jsondata = tweets.returnJSON()
    #print len(jsondata)

    #returning json data of the graph.
    return json.dumps(jsondata)



    #print "test: square(42) ==", square(42)
if __name__ == '__main__':
    #analyzeTweets('yahoo',50,"")
    
    #app.run(host='0.0.0.0', port=port)

#keyword = "taytweets"
##pass in a keyword from the ajax call, as well as dates, quantity, n% cutoff
## and so on.

##We both need filtering functions for the twitter firehose api, as well as
##a node filter function #functionalprogrammingyall
## and an edge filter function.

##also return json file to ajax caller.
