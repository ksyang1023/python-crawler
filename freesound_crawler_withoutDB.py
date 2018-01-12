import requests
import json
import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
import sys

from freesound_crawler import *
from freesound_account_info import *

if __name__ == '__main__':
	ACCESS_TOKEN =  getAccessToken();
	if ACCESS_TOKEN is None:
		print "Can't get access token"
		exit()

	MAX_PAGE = getMaxPage(ACCESS_TOKEN)
	from_page = 1
	to_page = MAX_PAGE
	if len(sys.argv) > 1:
		from_page = int(sys.argv[1])
	if len(sys.argv) > 2:
		to_page = int(sys.argv[2])
	crawling(ACCESS_TOKEN, None, from_page, to_page)
	print "Error log: ",error