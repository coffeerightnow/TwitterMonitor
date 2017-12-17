Twitter Media Monitor
=====================

About
--------
Twitter Media Monitor is an Webapplication to capture and visualize Relations between Hashtags as a Graph.
Furthermore it provides a view with quantity statistics.

Requirements
-------------------
Python >= V 3.5.2  - Tested with this version. May work properly with other V3.x
MongoDB server >= 3.4.9 

Installation
----------------

You canclone the repository from
Github and install it manually:

    git clone https://github.com/coffeerightnow/TwitterMonitor.git
    python setup.py sdist
    pip install twitter_monitor-1.x.tar.gz

Dependecies (Flask, Pymongo, Tweepy) will be installed after setup.

Configuration
-------------------
- Set the IP Addresses withtin **config.ini** File
Current implementation fits best with one searchterm (displayed as root node in the graph)
- Change the frontend files:
	- Webserver IP Addresses 
		- frontend.html: Line 10 
		- view1script.js: Line 3 
		- view2script.js: Line 12
- Current descriptions in frontend HTML is expecting blockchain as search term in config.ini You can change this according your needs.

Starting (Linux)
-----------
Start the Twitter Bot from Repository root directory to collect the tweets:

	python -m twitter_monitor.twitter_bot_runner & 

Start the Webserver from Repository root directory:
	
	sudo ../bin/python3.6 frontend/twitter_monitor_webapp.py &

	
Testing
----------
Run test from Repository root directoryand follow instruction within test file:
	
	python tests/integration_tester.py 

Logging
-----------
Logevents are stored in **twitter_log.log**
