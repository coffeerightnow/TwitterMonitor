import json
import unittest
import time
from twitter_monitor.config_loader import BackendConfig
from twitter_monitor.data_processing.twitter_data_collector import TweetProcessor, TweetQueue
from twitter_monitor.persistence.db_connector import DataQuery

""" Generate a certain quantity of tweets with different hashtags (searchterms) included. 
Write the tweets and its extracted metadata to the database named 'TEST'. 
We expect 'a' 500 times, 'b' 200 times, 'c' 300 times. Further 'a' and 'b' and 'c' 100 times together for one run 
of this integration test. To verify the test, check the data entries in db and verify the view in frontend"""


class TestDBQuery(unittest.TestCase):
    def setUp(self):
        self.config = BackendConfig()
        self.query = DataQuery(db_config=self.config.db_config)
        self.tweet_queue = TweetQueue()
        self.tweet_processor = TweetProcessor(tweet_queue=self.tweet_queue, config=self.config)
        self.tweet_processor.start()

    def test_quantity_for_a(self):
        result = self.query.get_top_hashtags(3)
        self.assertEqual(result[0]['hashtag'], 'a')
        self.assertEqual(result[0]['total_count'], 500)

    def test_quantity_for_b(self):
        result = self.query.get_top_hashtags(3)
        self.assertEqual(result[1]['hashtag'], 'c')
        self.assertEqual(result[1]['total_count'], 300)

    def test_quantity_for_c(self):
        result = self.query.get_top_hashtags(3)
        self.assertEqual(result[2]['hashtag'], 'b')
        self.assertEqual(result[2]['total_count'], 200)

    def test_relation_quantity_a_b(self):
        result = self.query.get_related_hashtags('a', 3)
        self.assertEqual(result[1]['hashtag_A'], 'a')
        self.assertEqual(result[1]['hashtag_B'], 'b')
        self.assertEqual(result[1]['total_count'], 200)

    def test_relation_quantity_a_c(self):
        result = self.query.get_related_hashtags('a', 3)
        self.assertEqual(result[0]['hashtag_A'], 'a')
        self.assertEqual(result[0]['hashtag_B'], 'c')
        self.assertEqual(result[0]['total_count'], 300)

    def test_relation_quantity_b_c(self):
        result = self.query.get_related_hashtags('b', 3)
        self.assertEqual(result[1]['hashtag_A'], 'b')
        self.assertEqual(result[1]['hashtag_B'], 'c')
        self.assertEqual(result[1]['total_count'], 100)

    def generate_test_tweets(self):
        """Generate tests tweets with the hashtag 'a', 'b' and 'c'"""

        for tweet in range(0, 100):
            tweet = {'entities': {'hashtags': [
                {'text': 'a'}
            ]}}
            self.tweet_queue.put_tweet(json.dumps(tweet))

        for tweet in range(0, 100):
            tweet = {'entities': {'hashtags': [
                {'text': 'a'},
                {'text': 'b'}
            ]}}
            self.tweet_queue.put_tweet(json.dumps(tweet))

        for tweet in range(0, 200):
            tweet = {'extended_tweet': {'entities': {'hashtags': [
                {'text': 'a'},
                {'text': 'c'}
            ]}}}
            self.tweet_queue.put_tweet(json.dumps(tweet))

        for tweet in range(0, 100):
            tweet = {'entities': {'hashtags': [
                {'text': 'a'},
                {'text': 'b'},
                {'text': 'c'}
            ]}}
            self.tweet_queue.put_tweet(json.dumps(tweet))

        for tweet in range(0, 100):
            tweet = {'entities': {'hashtags': [
                {'text': 'b'},
                {'text': 'c'}
            ]}}
            self.tweet_queue.put_tweet(json.dumps(tweet))


testcase = TestDBQuery();
testcase.setUp()
testcase.generate_test_tweets()
time.sleep(15) # let db store before run the test
unittest.main()
