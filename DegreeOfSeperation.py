"""
This program is a way to find out if any two actors have a relationship movie wise
Created for BrickHack4
1/28/18

Authors: Sean Bonaventure, Abhaya Tamrakar
"""


import requests
import json
import sys
import time
from collections import deque
from collections import namedtuple
class findSep:
    API_KEY = sys.argv[1]
    ALTERNATE_KEY = sys.argv[2]
    # List of movies Kevin Bacon was in so we can skip some steps
    targetMovies = list()

    # Contains the actors and movies that were checked
    checked = list()
    targetName = ""
    Actor = namedtuple("Actor", "name id perviousRelations")
    def getInput(self):
        print("Please try and spell the names correctly")
        self.targetName = input("What star is the target? ")
        startingPoint = input("What is the other star? ")
        targetId = self.findID(self.targetName, True)
        self.targetSetup(targetId)
        print("Finding connection")
        self.findID(startingPoint, False)

    def findID(self, actorName, target):
        """
        Finds ID of an actor
        :param actorName: The actor name
        :return: Movie id
        """
        actorID = ""
        with (open("cleaninput.json", 'r', encoding="utf8")) as actorList:
            for line in actorList:
                foundActor = json.loads(line)["name"]
                if actorName.lower() == foundActor.lower():
                    # print("Actor id: " + str(json.loads(line)["id"]))
                    actorID = str(json.loads(line)["id"])
        if target:
            return actorID
        else:
            startActor = self.Actor(actorName, actorID, [(actorName, "IDK")])
            return self.startSearch(startActor)

    def startSearch(self, startActor):
        """
        The main search method. It is basically a modified breadth first search, treating each actor and movie
        as a node in the graph. We start by seeing if the target and starting point share a common movie. If they don't
        we take the top 5 movies of the starting point and get the top 5 actors from all those movies. Then we put all
        of them in a queue. Then we go through the queue and see if the actors in the queue share a movie with the target.
        If they don't we take their top 5 movies and top 5 actors from each and put them in the same queue as earlier,
        and repeat the process
        :param startActor:
        :return:
        """
        # Checks to see if there is a direct link
        result = self.compareMovies(startActor.id)
        if result[0]:
            print(startActor.name + " was in " + str(result[1]) + " with " + self.targetName)
            return
        else:
            self.checked.append(startActor.id)
        """
        Once we get to this point we can assume that there is no direct connection between the two people.
        From this point we need to go into each individual movie and look at the cast members, and see if they have any 
        relation to Kevin Bacon. It is going to be a modified breadth first search
        """
        queue = deque()
        queue = self.addToQueue(queue, startActor)
        while len(queue) > 0:
            actor = queue.popleft()
            if actor.id not in self.checked:
                #print("Checking " + actor.name)
                result = self.compareMovies(actor.id)
                if result[0]:
                    # print("Found a match, both in " + result[1])
                    msg = startActor.name + " was in "
                    for i in range(1, len(actor.perviousRelations)):
                        msg = msg + actor.perviousRelations[i][1] + " with " + actor.perviousRelations[i][0] + " who was in "
                    msg = msg + str(result[1]) + " with " + self.targetName
                    print(msg)
                    return msg
                else:
                    queue = self.addToQueue(queue, actor)
                    self.checked.append(actor.id)

    def addToQueue(self, oldQueue, prevActor):
        """
        This basically handles the Queue for the breadth first search. If an actor has no direct relationship to the target
        then we take th top 5 cast members from their top 5 movies and put them in the queue to search for
        them later.
        You may notice the time.sleep(.1). That is because the API only allows 40 calls per 10 seconds so if i make too
        many calls i get locked out. I found if I .1 seconds between adding actors to the queue I won't hit the limit.
        I also created a second account and obtained a second key, and if I get locked out of one I switch to the other
        :param oldQueue: the old queue to be added to
        :param prevActor: The actor we are being referred from
        :return:
        """
        films = self.listOfFilms(prevActor.id)
        if len(films) > 5:
            max = 5
        else:
            max = len(films)
        for i in range(max):
            movieID = films[i][0]
            payload = {"api_key": self.API_KEY}
            url = "https://api.themoviedb.org/3/movie/" + str(movieID) + "/credits"
            r = requests.get(url, payload)
            time.sleep(0.1)
            #print("Movie url:" + r.url)
            try:
                cast = json.loads(r.text)["cast"]
            except:
                print(r.text)
                print("Switching Keys")
                self.switchKey()
                time.sleep(2)
                print("Done Sleeping")
            if len(cast) > 5:
                max2 = 5
            else:
                max2 = len(cast)
            for j in range(max2):
                oldList = prevActor.perviousRelations
                newList = oldList[:]
                newList.append((cast[j]['name'], films[i][1]))
                newActor = self.Actor(name=cast[j]['name'], id=cast[j]['id'], perviousRelations=newList)
                oldQueue.append(newActor)
        return oldQueue

    def targetSetup(self, id1):
        """
        This method find the id for all the movies the target is in so if we see one we have an immediate connection
        :return: nothing
        """
        params = {"api_key": self.API_KEY, "language": "en-US"}
        url = "https://api.themoviedb.org/3/person/" + str(id1) + "/movie_credits"
        try:
            r = requests.get(url, params)
        except:
            print("Switching Key")
            self.switchKey()
        cast = json.loads(r.text)["cast"]
        for i in range(len(cast)):
            # print("Kevin Bacon Movie ID: " + cast[i]["credit_id"])
            self.targetMovies.append((cast[i]["id"], cast[i]['original_title']))

    def compareMovies(self, actorID):
        """
        Finds out if the target and the current actor are in any similar movies
        :param actorID: The actors ID
        :return: If they are return true and the movie they share
        """
        movieList = self.listOfFilms(actorID)
        for i in range(len(movieList)):
            if movieList[0] not in self.checked:
                for j in range(len(self.targetMovies)):
                    if movieList[i][0] == self.targetMovies[j][0]:
                        return True, movieList[i][1]
                    else:
                        self.checked.append(movieList[i][0])
        return False, ""

    def listOfFilms(self, actorID):
        """
        This gets the list of films this current actor was in
        :return: a tuple with movie id and name
        """
        params = {"api_key" : self.API_KEY, "language" : "en-US"}
        url = "https://api.themoviedb.org/3/person/" + str(actorID) + "/movie_credits"
        try:
            r = requests.get(url, params)
        except:
            print("Switching Key")
            self.switchKey()
        #print(r.url)
        try:
            movies = json.loads(r.text)['cast']
        except:
            print(r.text)
            print("Switching key")
            self.switchKey()
        movieList = list()
        for i in range(len(movies)):
            if movies[i]['popularity'] > 4:
                movieList.append((movies[i]['id'], movies[i]['original_title']))
        return movieList

    def switchKey(self):
        pl = self.API_KEY
        self.API_KEY = self.ALTERNATE_KEY
        self.ALTERNATE_KEY = pl

finder = findSep()
finder.getInput()