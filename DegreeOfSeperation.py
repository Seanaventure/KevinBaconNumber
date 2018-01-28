import requests
import json
import sys
import time
from collections import deque
from collections import namedtuple
class findSep:
    kevinBacon = "Kevin Bacon"
    API_KEY = sys.argv[1]
    ALTERNATE_KEY = sys.argv[2]
    # List of movies Kevin Bacon was in so we can skip some steps
    kevinBaconMovies = list()

    # Contains the actors and movies that were checked
    checked = list()

    actor = namedtuple("actor", "name id perviousRelations")
    def getInput(self):
        self.actor = input("What celebrity would you like? ")
        print("Finding connection")
        self.findID(self.actor)

    def findID(self, actorName):
        """
        Finds ID of an actor
        :param actorName: The actor name
        :return: Movie id
        """
        actorID = ""
        with (open("cleaninput.json", 'r', encoding="utf8")) as actorList:
            for line in actorList:
                foundActor = json.loads(line)["name"]
                if actorName == foundActor:
                    print("Actor id: " + str(json.loads(line)["id"]))
                    actorID = str(json.loads(line)["id"])
        self.startSearch((actorID, actorName))

    def startSearch(self, startActor):

        # Checks to see if there is a direct link
        self.compareID()
        films = self.listOfFilms(startActor[0])
        if self.compareMovies(startActor[0])[0]:
            print("Done!")
            #return
        else:
            self.checked.append(startActor[1])
        """
        Once we get to this point we can assume that there is no direct connection between the two people.
        From this point we need to go into each individual movie and look at the cast members, and see if they have any 
        relation to Kevin Bacon. It is going to be a modified breadth first search
        """
        depth = 1
        queue = deque()
        queue = self.addToQueue(queue, films)
        print("added people to queue")
        while len(queue) > 0:
            actor = queue.popleft()
            one = actor['name']
            two = startActor[1]
            if one not in self.checked:
                print("Checking " + actor['name'])
                result = self.compareMovies(actor['id'])
                if result[0]:
                    print("Found a match, both in " + result[1])
                    return
                else:
                    queue = self.addToQueue(queue, self.listOfFilms(actor['id']))
                    self.checked.append(one)
    def addToQueue(self, oldQueue: deque, films):
        """
        This basically handles the Queue for the breadth first search. If an actor has no direct relationship to Kevin
        Bacon then we take th top 5 cast members from their top 5 movies and put them in the queue to search for
        them later.
        :param oldQueue:
        :param films:
        :return:
        """
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
                max = 5
            else:
                max = len(cast)
            for i in range(max):
                oldQueue.append(cast[i])
        return oldQueue

    def compareID(self):
        """
        This method find the id for all the movies Kevin Bacon is in so if we see one we have an immediate connection
        :return:
        """
        params = {"api_key": self.API_KEY, "language": "en-US"}
        url = "https://api.themoviedb.org/3/person/" + str(4724) + "/movie_credits"
        try:
            r = requests.get(url, params)
        except:
            print("Switching Key")
            self.switchKey()
        cast = json.loads(r.text)["cast"]
        for i in range(len(cast)):
            # print("Kevin Bacon Movie ID: " + cast[i]["credit_id"])
            self.kevinBaconMovies.append((cast[i]["id"], cast[i]['original_title']))

    def compareMovies(self, actorID):
        movieList = self.listOfFilms(actorID)
        for i in range(len(movieList)):
            if movieList[0] not in self.checked:
                for j in range(len(self.kevinBaconMovies)):
                    if movieList[i][0] == self.kevinBaconMovies[j][0]:
                        return True, movieList[i][1]
                    else:
                        self.checked.append(movieList[i][0])
        return False, ""

    def listOfFilms(self, actorID):
        """
        This gets the list of films this current actor was in
        :return:
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