import configparser
import logging

class BackendConfig:
    """Loads the relevant Backend Configuration from config.ini and offers an easy access"""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        # load search_terms
        self.search_terms = self.config['SEARCH_TERMS']['search_terms'].split()

        # load Twitter credentials
        self.twitter = dict()
        self.twitter['consumer_key'] = self.config['TWITTER']['consumer_key']
        self.twitter['consumer_secret'] = self.config['TWITTER']['consumer_secret']
        self.twitter['access_token_key'] = self.config['TWITTER']['access_token_key']
        self.twitter['access_token_secret'] = self.config['TWITTER']['access_token_secret']
        self.twitter['recovery_time'] = int(self.config['TWITTER']['recovery_time'])

        # load
        self.db_config = dict()
        self.db_config['host'] = self.config['DB_CONFIG']['host']
        self.db_config['port'] = int(self.config['DB_CONFIG']['port'])
        self.db_config['name'] = self.config['DB_CONFIG']['name']

        # Translate the LoggingLevel Strings into Logger loglevels
        self.__log_levels = dict()
        self.__log_levels['CRITICAL'] = logging.CRITICAL
        self.__log_levels['DEBUG'] = logging.DEBUG
        self.__log_levels['ERROR'] = logging.ERROR
        self.__log_levels['WARNING'] = logging.WARNING
        self.__log_levels['WARN'] = logging.WARN
        self.__log_levels['FATAL'] = logging.FATAL

        self.log_level = self.__log_levels[self.config['LOGGING']['loglevel']]

class WebserverConfig:
    """Loads the relevant Webserver Configuration from config.ini and offers an easy access"""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.webserver_host = self.config['WEBSERVER_CONFIG']['webserver_host']
        self.webserver_port = int(self.config['WEBSERVER_CONFIG']['webserver_port'])

