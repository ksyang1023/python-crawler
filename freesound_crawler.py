import requests
import json
import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
import sys

#usage: python freesound_crawler.py [from_page] [to_page]

SOUND_URL = "https://freesound.org/apiv2/sounds/"
SEARCH_URL = "https://freesound.org/apiv2/search/text/"
AUTORIZE_URL = "https://freesound.org/apiv2/oauth2/authorize"

#freesound account imformation
from freesound_account_info import * 

#mongo db imformation
from mongodb_info import * 

error = []
MAX_PAGE = 24086

#connect to mongodb, return None if connection failure
def getDB():
	try:
		client = MongoClient('mongodb://%s:%s@%s:%s/edudata' % (MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT))
		client.server_info()
		db = client.edudata
		return db.freesound
	except Exception as e:
		print "Unexpected error:", e
		return None



#send request with access token
def sendRequest(url, token):
	try:
		header = {'Authorization' : "Bearer " + token};
		res = requests.get(url, headers = header);
		return json.loads( res.text )
	except Exception as e:
		print "Failed to send request(" , url, "):", e
		error.append({'url':url, 'type':'send request'})
		return None

def getMaxPage(token):
	data = sendRequest(SEARCH_URL,token)
	try:
		return data['count']/ 15 + 1
	except:
		print ("Failed to update max page")
		return MAX_PAGE

#get sound info with access token
def getSoundInfo( sound_id, token ):
	try:
		data = {}
		sound_data = sendRequest(SOUND_URL + str(sound_id), token)
		if sound_data is None:
			raise Exception('json is none')
		data['_id'] = sound_data[ 'id' ];
		data['url'] = sound_data[ 'url' ];
		data['title'] = sound_data[ 'name' ];
		data['creator'] = sound_data[ 'username' ];
		data['createdate'] = sound_data[ 'created' ];
		data['description'] = sound_data[ 'description' ];
		data['download_url'] = sound_data['download']

		data['keyword'] = []
		for tag in sound_data[ 'tags' ]:
			data['keyword'].append(tag)
		data['previews'] = []
		for i in sound_data['previews'].keys():
			data['previews'].append({i:sound_data['previews'][i]})
			
		data['type'] = sound_data[ 'type' ];
		data['bitrate'] = sound_data[ 'bitrate' ];
		data['channels'] = sound_data[ 'channels' ];
		data['downlaod'] = sound_data[ 'num_downloads' ];
		data['license'] = sound_data[ 'license' ];
		data['filesize'] = sound_data[ 'filesize' ];
		return data;
	except Exception as e:
		print "Error occurs while getting sound info", sound_id, ": ", sys.exc_info()
		print sound_data
		return None

#execute queries 
def insertDB( db, query):
	if query is not None:
		result = db.bulk_write(query, ordered = False)
		print result.bulk_api_result


def crawling(token, db, page=1, page_to = MAX_PAGE):
	header = {'Authorization' : "Bearer " + token};

	print "From page", page, "to page", page_to
	for i in range(page, page_to + 1):
		if i > MAX_PAGE:
			print "Meet max page", MAX_PAGE
			break;
		url = SEARCH_URL + "?page=" + str(i)
		list_data = sendRequest(url, token)
		
		try:
			update_queries = []
			for d in list_data['results']:
				data = getSoundInfo( d['id'], token);
				if data is None:
					error.append({'id': d['id']});
					continue
				print data
				cuurent_time = datetime.datetime.utcnow();
				data['update_at'] = cuurent_time
				update_queries.append(UpdateOne({'_id':data['_id']}, {'$set': data, '$setOnInsert':{'created_at':cuurent_time}},True))
			if db is not None:
				insertDB(db, update_queries)

			print "Page", i, "is Done"
		except Exception as e:
			print "Error in page", i, ":", e
			error.append({'Exception':e, 'type':'parse data', 'data':list_data})
			print list_data
		page += 1


if __name__ == '__main__':
	db = getDB();
	if db is None:
		print "No db connected"
		exit()
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
	crawling(ACCESS_TOKEN, db, from_page, to_page)
	print "Error log: ",error