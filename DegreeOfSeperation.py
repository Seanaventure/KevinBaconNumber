import requests
import json
import sys
import time
from collections import deque
class findSep:
    kevinBacon = "Kevin Bacon"
    API_KEY = sys.argv[1]

    # List of movies Kevin Bacon was in so we can skip some steps
    kevinBaconMovies = list()

    # Contains the actors and movies that were checked
    checked = list()

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
            self.checked.append(startActor[0])
        """
        Once we get to this point we can assume that there is no direct connection between the two people.
        From this point we need to go into each individual movie and look at the cast members, and see if they have any 
        relation to Kevin Bacon. It is going to be a modified breadth first search
        """
        depth = 1
        queue = deque()
        queue = self.addToQueue(queue, films)
        while len(queue) > 0:
            actor = queue.popleft()
            result = self.compareMovies(actor['name'])
            if result[0]:
                print("Found a match, both in" + result[1])
            else:
                queue = self.addToQueue(queue, self.listOfFilms(actor['id']))
            # for i in range(len(films)):
            #     print("Searching " + str(films[i][1]))
            #     movieID = films[i][0]
            #     payload = {"api_key":self.API_KEY}
            #     url = "https://api.themoviedb.org/3/movie/" + str(movieID) + "/credits"
            #     r = requests.get(url, payload)
            #     cast = json.loads(r.text)["cast"]
            #     max = 0
            #     if len(cast) > 10:
            #         max = 10
            #     else:
            #         max = len(cast)
            #     for j in range(max):
            #         if cast[j]['id'] not in self.checked:
            #             result = self.compareMovies(cast[j]['id'])
            #             print("Checking " + cast[j]['name'])
            #             if result[0]:
            #                 print(startActor[1] + " was in " + films[i][1] + " with " + cast[j]['name'] + " who is in " + str(result[1]) + " with Kevin Bacon. Depth: " + str(depth))
            #                 return
            #             else:
            #                 print(cast[j]['name'] + " was added to queue ")
            #                 queue.append(cast[j])
            #                 self.checked.append(cast[j][id])
            #         else:
            #             print("Going in a level deeper after " + cast[j]['name'])

            depth += 1
            print("Depth increasing. Now it is " + str(depth))
    def addToQueue(self, oldQueue: deque, films):
        for i in range(len(films)):
            movieID = films[i][0]
            payload = {"api_key": self.API_KEY}
            url = "https://api.themoviedb.org/3/movie/" + str(movieID) + "/credits"
            r = requests.get(url, payload)
            cast = json.loads(r.text)["cast"]
            max = 0
            if len(cast) > 10:
                max = 10
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
        r = requests.get(url, params)
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
        r = requests.get(url, params)
        try:
            movies = json.loads(r.text)['cast']
        except:
            print("API call limit reached")
            time.sleep(10000)
            return
        movieList = list()
        for i in range(len(movies)):
            if movies[i]['popularity'] > 8:
                movieList.append((movies[i]['id'], movies[i]['original_title']))
        return movieList

finder = findSep()
finder.getInput()