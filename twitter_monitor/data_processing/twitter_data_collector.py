import json
import logging
import logging.handlers
import time
from queue import Queue, Empty
from threading import Thread
import tweepy
from ..persistence.db_connector import DataPersistor
from ..config_loader import BackendConfig


class TweetQueue:
    """Queue for temporarly storing the tweets."""

    def __init__(self):
        self.queue = Queue(200)
        self.time_of_last_tweet = time.time()

    def put_tweet(self, data):
        self.time_of_last_tweet = time.time()
        self.queue.put(data)

    def get_tweet(self):
        return self.queue.get(timeout=120)

    def get_seconds_since_last_tweet(self):
        return (time.time() - self.time_of_last_tweet)


class TwitterStreamListener(tweepy.StreamListener):
    """Twitter StreamListener Class"""

    def __init__(self, tweet_queue: TweetQueue, config:BackendConfig):
        auth = tweepy.OAuthHandler(config.twitter['consumer_key'], config.twitter['consumer_secret'])
        auth.set_access_token(config.twitter['access_token_key'],
                              config.twitter['access_token_secret'])
        self.api = tweepy.API(auth)
        self.twitterStream = tweepy.Stream(auth=self.api.auth, listener=self)
        self.search_terms = ['#' + term for term in config.search_terms]
        self.tweet_queue = tweet_queue
        self.time_of_last_tweet = time.time()
        logging.basicConfig(format='%(asctime)s %(message)s', level=config.log_level, filename='twitter_log.log')

    def start_listener(self):
        """Use this Method to start capturing Data from Twitter."""

        try:
            logging.debug("Starting the Twitter Streamlistener... ")
            self.twitterStream.filter(track=self.search_terms, async=True)
        except tweepy.TweepError as exp:
            logging.critical("Exception in filter loop. ", exp)

    def on_connect(self):
        """This method is initially called when the client is connected to the Twitter Stream API"""
        logging.critical("Connected to the streaming API.")

    def on_status(self, status):
        logging.critical("on status called: ", status)

    def on_error(self, status_code):
        """On error - if an error occurs, display the error / status code"""
        logging.critical('An Error has occured: ' + repr(status_code))

    def on_data(self, data):
        """This method is called by the API as soon a new tweets arrives which is matching the filter criteria.
        Adding the tweet into tweet queue"""
        self.time_of_last_tweet = time.time()
        self.tweet_queue.put_tweet(data)

    def on_timeout(self):
        """Called when stream connection times out"""
        logging.critical('An Timeout has occured.')

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice"""
        logging.critical('Twitter has called "on Disconnect has occured. Message: ', notice)

    def on_closed(self, resp):
        """Called when twitter sends a disconnect notice"""
        logging.critical('Twitter has called "on closed". Message: ', resp)

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        logging.critical('Twitter called "on_limit". Message: ', track)

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        logging.critical('Twitter  called "on_warning". Message: ', notice)

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        logging.critical('Twitter  called "on_exception". Message: ', exception)


class TweetProcessor(Thread):
    """This class classifies the tweets and hands the over ro the db_client for persisting"""

    def __init__(self, tweet_queue: TweetQueue, config:BackendConfig):
        Thread.__init__(self, daemon=True)
        logging.basicConfig(format='%(asctime)s %(message)s', level=config.log_level, filename='twitter_log.log')
        self.db_client = DataPersistor(config.db_config)
        self.search_terms = config.search_terms
        self.tweet_queue = tweet_queue
        self.alive = True

    def set_dead(self):
        self.alive = False

    def run(self):
        """dequeuing tweets and persist them to db."""

        while self.alive:
            search_term_as_hashtag = False

            # get tweet from queue if there are available
            try:
                tweet = self.tweet_queue.get_tweet()
            except Empty:
            # nothing in queue, check alive flag again
                continue

            # Decode the JSON from Twitter
            tweet_json = json.loads(tweet)

            # Check if its an extended Tweet with >140 Character, because structure of json is different
            # get all hashtag words from the tweet in a set
            if 'extended_tweet' in tweet_json:
                # check if its a extended tweet.
                hashtags = {d['text'].lower() for d in tweet_json['extended_tweet']['entities']['hashtags']}
            else:
                if 'entities' in tweet_json: # safety check that there is the needed key in dict.
                    hashtags = {d['text'].lower() for d in tweet_json['entities']['hashtags']}
                else:
                    logging.critical("The arrived Tweet does not have the expected structure. It cannot be processed")
                    continue

            for word in hashtags:
                if word in self.search_terms:
                    search_term_as_hashtag = True

            # check if the tweets contains the at least one of the searchterms. Otherwise don't persist.
            # Tweepy API deliveres also tweets without having the searchterm in the Hashtags
            # (i.e hashtag in user profile description)
            if not search_term_as_hashtag:
                continue
            else:
                # pass data to the db client
                try:
                    self.db_client.insert_to_db(tweet_json, hashtags)
                except Exception as e:
                    logging.critical("Exception in writing to db: ", e)
