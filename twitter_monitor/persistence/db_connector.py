import itertools
import json
from datetime import date
from bson.json_util import dumps
from pymongo import MongoClient
from pymongo import UpdateOne

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class MongoDBConnector(metaclass=Singleton):
    def __init__(self, config: dict):
        self.client = MongoClient(config['host'],
                                  config['port'],
                                  serverSelectionTimeoutMS=1000)

        self.db = self.client[config['name']]


class DataPersistor:
    def __init__(self, config: dict):
        self.db_connection = MongoDBConnector(config)
        self.db = self.db_connection.db

    def insert_to_db(self, tweet: str, hashtags: set) -> None:
        """insert data into db within three steps"""

        # increase the count in the hashtag_counts collection for each hashtag in the set
        self.db.hashtag_counts.bulk_write([UpdateOne(
            {'hashtag': hashtag},
            {"$inc": {"total_count": 1,
                      "daily_count." + date.today().strftime('%Y-%m-%d'): 1}},
            upsert=True) for hashtag in hashtags])

        # increase the count in the hashtag_relationsship_counts for all pairs of hashtags
        if len(hashtags) > 1:
            hashtag_tuples = list(itertools.combinations(sorted(hashtags), 2))
            self.db.hashtag_relationship_counts.bulk_write([UpdateOne(
                {'hashtag_A': hashtag_tuple[0],
                 'hashtag_B': hashtag_tuple[1]},
                {"$inc":
                     {"total_count": 1, "daily_count." + date.today().strftime('%Y-%m-%d'): 1}},
                upsert=True) for hashtag_tuple in hashtag_tuples])

        # insert the tweet itself to the tweets collection
        self.db.tweets.insert(tweet)


class DataQuery:
    """Class which is offering some methods to get Data from database"""

    def __init__(self, db_config):
        self.db_connection = MongoDBConnector(db_config)
        self.db = self.db_connection.db

    def get_top_hashtags(self, quantity: int) -> json:
        """get the most popular hashtags with their counts. Specify the limit quantity to return."""

        db_query = self.db.hashtag_counts.find().sort("total_count", -1).limit(quantity)
        json_response = json.loads(
            dumps(db_query))  # load string into json list. dumps loads a string from bson cursor object.
        return json_response

    def get_related_hashtags(self, hashtag: str, quantity: int) -> json:
        """get the hashtags which are in the same tweet as the given tweet. add 1, beacause root ist also counted.
        We want quantity of leafes"""

        db_query = self.db.hashtag_relationship_counts.find(
            {"$or": [{"hashtag_A": hashtag}, {"hashtag_B": hashtag}]}).sort("total_count", -1).limit(quantity + 1)
        json_response = json.loads(
            dumps(db_query))  # load string into json list. dumps loads a string from bson cursor object.
        return json_response

    def get_total_tweet_count(self) -> int:
        """get the current quantitiy of persisted tweets in the DB"""
        db_query = self.db.tweets.count()
        total_tweet_count = json.loads(
            dumps(db_query))  # load string into json list. dumps loads a string from bson cursor object.
        return total_tweet_count

    def get_one_tweet(self):
        db_query = self.db.tweets.find_one()
        json_response = json.loads(
            dumps(db_query))  # load string into json list. dumps loads a string from bson cursor object.
        return json_response
