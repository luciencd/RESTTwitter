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
#NLTK_DATA = '/Users/lucienchristie-dervaux/documents/RESTTwitter'
nltk.data.path.append('/Users/lucienchristie-dervaux/documents/RESTTwitter/nltk_data')
nltk.data.path.append('/home/vcap/app/nltk_data')
nltk.data.path.append('/Users/luciencd/Dropbox/Ibm/Documents/RESTTwitter/nltk_data')
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
    def invalidate(self,number):
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
    ## make it so we only get node greater than 0 mass with neighbors
    ## make it a functional programming option.
    def scrub(self):


        unordered_list = []
        for name,node in self.nodes.iteritems():
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

        for node in unordered_list:
            #print node.name,node.mass,len(node.neighbors)
            if(len(node.neighbors) == 0 or node.mass <= 0):
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


    def filtermain(self):
        ##create map of groups of nodes, rank them by size, choose greatest,
        ##then remove everything else.

        ##breadth first-search.
        if(self.size <=0):
            return False


        index = 0

        groups = 0
        maxnode = self.nodes.items()[0][1]
        #
        for name,node in self.nodes.items():
            #print node.neighbors
            node.visited = False
            if(len(node.neighbors) > len(maxnode.neighbors)):
                maxnode = node

        #print maxnode.dupes,maxnode.uniques


        #print maxnode.neighbors.items()
        group = -1
        groups = []
        while(index < len(self.nodes)):
            #print "firstnode",graph.nodes.items()[index][1]
            if(self.nodes.items()[index][1].visited == True):
                index+=1
                continue

            group+=1
            visited = {}
            queue = [self.nodes.items()[index][1]]
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

        for name,node in self.nodes.items():
            #print node
            if name not in visited:
                #print name,len(node.neighbors)
                node.valid = False
                for key,value in node.neighbors.iteritems():
                    value.valid = False

    ##Difficult to tell what is happening here,
    ##however, it
    def filteredges(self,graph):
        for name,node in graph.nodes.items():
            neighbor_array = node.neighbors.values()
            for edge in neighbor_array:
                edge.valid = False


        ##Here,
        for name,node in graph.nodes.items():

            neighbor_array = node.neighbors.values()

            neighbor_array = sorted(neighbor_array,key=lambda edge:edge.weight,reverse=False)


        for name,node in graph.nodes.items():

            neighbor_array = node.neighbors.values()
            index = 0
            for edge in neighbor_array:

                source_array = edge.source.neighbors.values()
                target_array = edge.target.neighbors.values()
                #print len(source_array),len(target_array)
                #print source_array,target_array
                #print edge.source,edge.target

                #getting rid of edges that are not relevant.
                '''
                if(source_array.index(edge)<= len(source_array)/2 or target_array.index(edge)<= len(target_array)/2):
                    edge.valid = True
                    '''
                '''
                if(index <= 15):
                    edge.valid = True

                index +=1
                '''

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

        ##Parameters
        self.keyword = keyword
        self.numTweets = numTweets


        ##JSON data
        self.twe = {}
        self.sentiments = {}
        self.output = {}

        ##Place to hold graph.
        self.graph = Graph()

        ##actual size of graph, maybe hold this value inside graph instead.
        self.size = -1

        ##dictionary that tells you the frequency of each word.
        self.df = {}
        
    def fetchTweets(self):
        ##Setting up API call
        payload = {"q": self.keyword, "size": self.numTweets}
        response = requests.get("https://cdeservice.mybluemix.net:443/api/v1/messages/search", params=payload, auth=(self.TWITTER_USERNAME, self.TWITTER_PASSWORD))


        ##loading in response of json data to class.
        twe = json.loads(response.text)
        self.twe = twe['tweets']
        return twe['tweets']
        
    def reduceit(self,string):
        #print string
        if(len(string) < 2):
            return ""
        string = string[0]+re.sub(r'\W', '', string[1:])
        #print string
        return string

    ##Taking in a set of tokens from a tweet, and adding it to the graph.
    def addToGraph(self,sentiment,tokens):

        #print "tweet:",body
        #print "content: ",hashtags+handle
        #print "handle:",handle
        for item in tokens:
            ##Add or edit the node itself
            oldnode = ""
            if(self.graph.nodeExists(item)):
                #getting node object from graph
                oldnode = self.graph.getNode(item)
            else:
                #creatig new node object.
                node = Node(item,0,1)
                self.graph.addNode(node)
                oldnode = self.graph.getNode(item)

            oldnode.mass += 1
            if(sentiment == 0):
                oldnode.anger+=1
            elif(sentiment == 1):
                oldnode.happiness+=1

            oldnode.count += 1

        ##Assigning a connection between the nodes that are in the set of nodes.
    
        for node1 in tokens:
            for node2 in tokens:
                if(node1 != node2):

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


    
    def createGraph(self,tweets):
        ##find out the sentiment of each tweet by going through the json object.
        for i in range(self.numTweets):
            #print i,len(tweets),len(tweets[i])



            ##At this point, we should have an object which using polymorphism,
            ##can have its body, and sentiment extracted

            ##That way, we can use this on facebook posts, and yelp reviews too.

            ##tweet = tweets[i]
            
            body = []
            try:
                ##From base object, should be able to get body.
                body = tweets[i]['message']['body']
            except KeyError:
                pass
            except IndexError:
                pass
            
            sentiment = ""
            try:
                sentiment = tweets[i]['cde']['content']['sentiment']['polarity']
            except KeyError:
                pass
            except IndexError:
                pass
            
            ##Get sentiment directly from tweet
            sentiment = self.getSentiment(sentiment)
            #print sentiment

            ##get tokens from body of text
            tokens = self.tokenize(body)
            #print tokens
            
            ##assign scores to the relevant tokens
            scores = self.scoreize(tokens)
            #print scores

            self.addToGraph(sentiment, scores)
    
            
    def getSentiment(self,sentiment):
        ##ideally compile all words here to begin with to get idf score

        #print "SENTIMENT",sentiment
        if(sentiment == "POSITIVE"):
            return 1
        elif(sentiment == "NEGATIVE"):
            return 0
        else:
            return 0.5


        


        

    def collectText(self,tweets):

        listOfWords = []

        for i in range(len(tweets)):
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

                if(normalizedToken != self.keyword[1:]):
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


            #print '{"name":',node.name,',"group":',node.group,',"mass":',node.mass,',"value":',node.value#node.neighbors#,node.value
            nodejson = {'name':node.name,'group':node.group,'value':len(node.neighbors),'sentiment':node.getSentiment()}

            #print {'name':item.name,'group':item.group,'size':item.size}

            #print 'json','name',item['name'],'group',item['group'],'size',item['size']
            nodesjsonlist.append(nodejson)
        jsonObj['nodes'] = nodesjsonlist

        edgesjsonlist = []
        for edge in self.graph.outputEdges():

            #print {'source':edge.source.value,'target':edge.target.value,'weight':edge.weight}
            edgejson = {'source':edge.source.value,'target':edge.target.value,'value':edge.weight,'sentiment':edge.getSentiment()}
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



    twittergraph = twitter(keyword,numTweets)
    ##dont bother with keyword and numTweets arguments.



    ##put all tweets in list.
    tweets = twittergraph.fetchTweets()
    print "fetchtweets"

    ##create text collection
    twittergraph.collectText(tweets)
    print "collecttext"
    ##get all the sentiment for nodes and generate graph.
    twittergraph.createGraph(tweets)
    print "getSentiment"



    ##reset all nodes to unfiltered unvisited.
    twittergraph.graph.reset(twittergraph.graph)
    print "reset"
    print len(twittergraph.graph.nodes)



    ##only allowing 5 top edges per node.
    ##tweets.graph.filteredges(tweets.graph)


    ##filtering things based on get requests
    if(mainBool == "True"):
        ##filter out all the nodes that are not a part of the biggest connected graph
        twittergraph.graph.filtermain()

    print "filtering"

    ##getting number of top bubbles to display.
    if(numBubbles > 0):
        ##filter only leaving top n nodes.
        twittergraph.graph.invalidate(numBubbles)

    if(numBubbles > 0):
        ##filter only leaving nodes that are greater than 0 mass with 0 neighbors
        twittergraph.graph.scrub()

    

    print "numbering bubbles"
    ##filter only leaving top n nodes.
    #tweets.graph.invalidate(tweets)



    twittergraph.graph.renameOrdered()
    jsondata = twittergraph.returnJSON()
    #print len(jsondata)

    #returning json data of the graph.
    print "finished"
    return json.dumps(jsondata)



    #print "test: square(42) ==", square(42)
if __name__ == '__main__':
    #analyzeTweets('yahoo',50,"")

    app.run(host='0.0.0.0', port=port)

#keyword = "taytweets"
##pass in a keyword from the ajax call, as well as dates, quantity, n% cutoff
## and so on.

##We both need filtering functions for the twitter firehose api, as well as
##a node filter function #functionalprogrammingyall
## and an edge filter function.

##also return json file to ajax caller.
