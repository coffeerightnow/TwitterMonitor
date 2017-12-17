# Starting Script of Twitter Monitor Webservice.
# Provides HTTP Endpoints to query the JSON Data from twitter_monitor application.

from twitter_monitor import TwitterMonitor
from twitter_monitor import WebserverConfig
from flask import Flask, jsonify, make_response, request

config = WebserverConfig()

app = Flask(__name__, static_folder='../frontend')
twitter_mon = TwitterMonitor()

# all of the pages are connected to a python function

@app.route('/')
def index():
    return app.send_static_file('frontend.html')


@app.route('/gettweetcount')
def get_tweet_count():
    return jsonify(twitter_mon.get_tweet_count())


@app.route('/hashtag/<int:quantity>')
def get_top_hashtags_json(quantity):
    return jsonify(twitter_mon.get_top_hashtags(quantity))


@app.route('/expanded_tree', methods=['GET'])
def expand_tree():
    quantity = int(request.args.get('quantity'))
    hashtag = request.args.get('hashtag')
    return jsonify(twitter_mon.expand_tree(quantity, hashtag))


@app.route('/hashtagsearch', methods=['GET'])
def hashtag_search():
    quantity = int(request.args.get('quantity'))
    hashtag = request.args.get('hashtag')
    return jsonify(twitter_mon.hashtag_search(quantity, hashtag))


@app.route('/timeline/<int:quantity>')
def get_timeline(quantity):
    return jsonify(twitter_mon.get_timeline(quantity))


@app.route('/termlist/<int:quantity>')
def get_hashtag_list(quantity):
    return jsonify(twitter_mon.get_hashtag_list(quantity))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found, PAWI'}), 404)


if __name__ == "__main__":  # start this webserver.
    app.run(host=config.webserver_host, port=config.webserver_port)
