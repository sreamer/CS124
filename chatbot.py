#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re

# add in PorterStemmer from assignment 3/4
from PorterStemmer import PorterStemmer

import numpy as np

from movielens import ratings
from random import randint


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
        self.name = 'moviebot'
        self.is_turbo = is_turbo
        # self.seekingMovie is meant to be true when looking for another movie recommendation from the user.
        # if the input does not contain another movie recommendation it will ask the user again for one.
        self.seekingMovie = False
        self.ratedmovies = {}
        self.titleDict = {}
        self.countMovieRecs = 0;
        self.unratedmovies = []
        self.read_data()
        self.porter = PorterStemmer()
        self.positiveSet = set()
        self.negativeSet = set()
        self.sentimentBuilder()
        # %sis replaced with movie title in responses
        self.PositiveResponse = ["It seems like you enjoyed %s. Maybe I should see it some time.",
                                 "Wow! I'm so glad you enjoyed %s. I love when people find things they like.",
                                 "Fantastic! Maybe we can watch %s together some time! After all, you liked it!",
                                 "My programmer also likes %s",
                                 "It's good to see that you found %s to be a good movie"]
        self.NegativeResponse = ["Yikes! Remind me to not see %s",
                                "I'm sorry that you didn't like %s",
                                 "I also didn't like %s"]


    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
        """chatbot greeting message"""
        #############################################################################
        # TODO: Write a short greeting message                                      #
        #############################################################################

        greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."
        self.seekingMovie = True
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

        return greeting_message

    def goodbye(self):
        """chatbot goodbye message"""
        #############################################################################
        # TODO: Write a short farewell message                                      #
        #############################################################################

        goodbye_message = 'Have a nice day!'

        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

        return goodbye_message

    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################
    def sentimentBuilder(self):
        file = open("data/sentiment.txt", "r")
        count = 0
        for x in self.titles:
            self.titleDict[x[0]] = count;
            count += 1;

        for line in file.readlines():
            lineInfo = line.split(",")
            word = lineInfo[0]
            evaluation = lineInfo[1].rstrip()
            if evaluation == "pos":
                self.positiveSet.add(self.porter.stem(word))
            if evaluation == "neg":
                self.negativeSet.add(self.porter.stem(word))
                # print self.positiveSet

    def sentimentAnalysis(self, input, movie):
        positiveScore = 0;
        negativeScore = 0;
        for word in input.split(" "):
            word = self.porter.stem(word)
            # print word
            if word in self.positiveSet:
                positiveScore += 1
            if word in self.negativeSet:
                negativeScore += 1
        # print positiveScore
        # print negativeScore
        if positiveScore > negativeScore:
            self.ratedmovies[self.titleDict[movie]] = 1;
            self.countMovieRecs += 1;
            return "I liked"
        if negativeScore > positiveScore:
            self.ratedmovies[self.titleDict[movie]] = -1;
            self.countMovieRecs += 1;
            return "I did not like"
        if (positiveScore == 0 and negativeScore == 0) or (positiveScore == negativeScore):
            return "I can't tell"

    def extractMovie(self, input):
        movies = re.findall("\"([^\"]*)\"", input)
        if len(movies) == 0:
            movies = self.extractUnquotedMovies(input)
        if len(movies) != 1:
            return "Please tell us about one movie"
        movie = movies[0]
        if movie not in self.titleDict:
            return "We can't find that movie in our database. Perhaps you can tell us about another one"
        if (self.countMovieRecs == 5):
            return "Top Movie: " + str(self.ratingmovie()[0])
        return movie + self.sentimentAnalysis(input, movie) + str(self.countMovieRecs)

    # returns all the movie titles that were in the input
    # need to add case insensitivity and not needing the year at the end. Don't know if that should happen in self.titleDict or something
    # also we need to make sure we aren't using words in movie titles in our sentiment analysis
    def extractUnquotedMovies(self, input):
        movies = []
        input_list = input.split(' ')
        possible_movies = []

        # searches for capitalized words or numbers for the beginning of a title
        for i, word in enumerate(input_list):
            if word[0].isupper() or word[0] in '0123456789':
                # makes sublists of all the possible titles beginning with that word
                sublists = [sublist for sublist in
                            (input_list[i:i + length] for length in xrange(1, len(input_list) - i + 1))]
                possible_movies.extend(sublists)

        for movie in possible_movies:
            movie = ' '.join(movie)

            # checks to see if any of the sublists are in our list of movies
            if movie in self.titleDict:
                movies.append(movie)
        return movies

    def process(self, input):
        """Takes the input string from the REPL and call delegated functions
        that
          1) extract the relevant information and
          2) transform the information into a response to the user
        """
        #############################################################################
        # TODO: Implement the extraction and transformation in this method, possibly#
        # calling other functions. Although modular code is not graded, it is       #
        # highly recommended                                                        #
        #############################################################################
        response = "no response"

        response = self.extractMovie(input)

        return response

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
        """Reads the ratings matrix from file"""
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, self.ratings = ratings()
        reader = csv.reader(open('data/sentiment.txt', 'rb'))
        self.sentiment = dict(reader)
        self.binarize()
        # print self.titles
        # print len(self.titles)
        # print len(self.ratings)
        # self.distance(self.ratings[1], self.ratings[2])
        # self.distance(self.ratings[10], self.ratings[0])
        self.ratingmovie()

    def binarize(self):
        """Modifies the ratings matrix to make all of the ratings binary"""
        # for the homework, take the utility matrix,
        # subtract the means of each of the rows, from the actual values of the ratings
        # then use it for binarized
        # -1 if less than mean
        # 0 if no ratings
        # +1 if greater than means


        # print self.ratings
        # for row in self.ratings:
        for row in range(0, len(self.ratings)):
            # print len(row)
            # print row
            rate = np.array(self.ratings[row])
            totalratings = 0
            totallenminus0 = 0
            for rating in rate:
                # print rating
                if rating != 0:
                    totalratings += rating
                    totallenminus0 += 1
            if totallenminus0 != 0:
                mean = totalratings / totallenminus0
                # mean = np.mean(rate)
                # print mean
                zerocentered = rate
                for i in range(0, len(zerocentered)):
                    if zerocentered[i] != 0:
                        zerocentered[i] -= mean
                # zerocentered = rate - mean
                # print zerocentered
                binarized = [np.sign(x) for x in zerocentered]
                print
                self.titles[row]
                print
                binarized
                self.ratings[row] = binarized

    def distance(self, u, v):
        """Calculates a given distance function between vectors u and v"""
        # TODO: Implement the distance function between vectors u and v]
        # Note: you can also think of this as computing a similarity measure
        # are we guarenteed that the vector lengths will be the same

        # similarity = cosine similarity on the binarized NOT pearson

        dotproduct = 0
        totalu = 0
        totalv = 0
        for i in range(0, len(u)):
            dotproduct += u[i] * v[i]
            totalu += u[i] ** 2
            totalv += v[i] ** 2
        if totalu == 0 or totalv == 0:
            return 0
        dist = float(dotproduct) / (math.sqrt(totalu) * math.sqrt(totalv))
        # print dist
        return dist
        # pass

    def recommend(self, u):
        """Generates a list of movies based on the input vector u using
        collaborative filtering"""
        # TODO: Implement a recommendation function that takes a user vector u
        # and outputs a list of movies recommended by the chatbot

        pass

    def ratingmovie(self):
        highestrating = 0
        topmovie = ""
        # subtracts all movies indexes with movies that we've seen to only have unrated movie indexes
        self.unratedmovies = list(set(xrange(0, len(self.titles))) - set(self.ratedmovies.keys()))
        # print self.unratedmovies
        for unratedmov in self.unratedmovies:
            rating = 0
            for ratedmov in self.ratedmovies:
                # print self.ratings[unratedmov]
                # print '\n'
                # print self.ratings[ratedmov]
                dist = self.distance(self.ratings[unratedmov], self.ratings[ratedmov])
                if dist > 0:
                    rating += dist * self.ratedmovies[ratedmov]
            if rating > highestrating:
                highestrating = rating
                topmovie = self.titles[unratedmov]
        # print topmovie
        return topmovie

    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
        """Returns debug information as a string for the input string from the REPL"""
        # Pass the debug information that you may think is important for your
        # evaluators
        debug_info = 'debug info'
        return debug_info

    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
        return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """

    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
        return self.name


if __name__ == '__main__':
    Chatbot()