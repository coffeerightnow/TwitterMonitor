import logging
from .config_loader import BackendConfig
import time
from .data_processing import TwitterStreamListener, TweetProcessor, TweetQueue

# load configuration
config = BackendConfig()
# setup Logging
logging.basicConfig(format='%(asctime)s %(message)s', level=config.log_level, filename='twitter_log.log')

# create TweetQueue to buffer the incoming tweets
tweet_queue = TweetQueue()

# start the twitter bot for collecting tweets into the tweet queue
twitter_bot = TwitterStreamListener(tweet_queue=tweet_queue, config=config)
tweet_processor = TweetProcessor(tweet_queue=tweet_queue, config=config)
tweet_processor.start()

# starting the tweet_processor thread for dequeuing the tweets and persist them to db.
twitter_bot.start_listener()

# recovery mechanism
while True:
    if tweet_queue.get_seconds_since_last_tweet() > config.twitter['recovery_time']:
        # close connection
        logging.critical(
            "restarting Twitter Listener and data Processor because more than "
            "recovery_time no Tweets arrived.")
        try:
            twitter_bot.twitterStream.disconnect()
            logging.critical("Twitter Stream disconntected...")
            tweet_processor.set_dead()
            tweet_processor.join()
        except:
            logging.critical("Twitter Stream disconntect was not possible.")

        # restart
        tweet_queue = TweetQueue()

        tweet_processor = TweetProcessor(tweet_queue=tweet_queue, config=config)
        tweet_processor.start()
        twitter_bot = TwitterStreamListener(tweet_queue=tweet_queue, config=config)
        twitter_bot.start_listener()

    logging.debug("Time passed since last tweet arrived")
    logging.debug(tweet_queue.get_seconds_since_last_tweet())
    time.sleep(60)
