from setuptools import setup
from setuptools import find_packages

setup(
    name='twitter_monitor',
    version='1.1',
    description='Tool for collecting  and visualize Twitter Data',
    author='Sandro Bernasconi, Eric Brun',
    author_email='Sandro.Bernasconi@hslu.ch',
    url='blockchainmediamonitor.enterpriselab.ch',
    packages=find_packages(),
    install_requires=['Flask', 'pymongo', 'tweepy']
)
