from bs4 import BeautifulSoup
import requests
import datetime
from pymongo import MongoClient, UpdateOne
import sys

URL_BYDATE = "https://openclipart.org/bydate?page="
URL_BASE = "https://openclipart.org"
URL_DOWNLOAD = "https://openclipart.org/download"


#mongo db imformation
from mongodb_info import * 

MAX_PAGE = 4168

error = []

#connect to mongodb, return None if connection failure
def getDB():
	try:
		client = MongoClient('mongodb://%s:%s@%s:%s/edudata' % (MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT))
		client.server_info()
		db = client.edudata
		return db.openclipart
	except Exception as e:
		print "Unexpected error:", e
		return None


#execute queries collecting from a page
def insertDB( openclipart, query):
	if query is not None:
		result = openclipart.bulk_write(query, ordered = False)
		print result.bulk_api_result



#get max page numbers
def updatePage( content ):
	try:
		res = requests.get(URL_BYDATE + str(1));	
		soup = BeautifulSoup(res.text, "lxml");
		content = soup.body.find(id="bydate");
		return int(content.find(attrs={"class" : "pagination_last"}).a["href"].split("=")[1])
	except Exception as e:
		return MAX_PAGE

#get data from a page and turn them into queries
def getData(pageNum):
	try:
		res = requests.get(URL_BYDATE + str(pageNum));	
		soup = BeautifulSoup(res.text, "lxml");
		content = soup.body.find(id="bydate");
		if content is None:
			raise Exception("Null content")
	except Exception as e:
		print "Can't get page ", pageNum,":",e
		error.append({"url":URL_BYDATE + str(pageNum), 'type':'get page', 'Exception': e})
		return None

	update_queries = []

	for element in content.find_all(attrs={"class" : "r-img"}):
		try:
			url = URL_BASE + element.a["href"]
			res2 = requests.get(url);	
			soup2 = BeautifulSoup(res2.text,"lxml");
			content2 = soup2.body.find(id="view");

			data = {}
			data['_id'] = element.a["href"].split("/", 2)[2];
			if content2.h2 is not None:
				data['title'] = content2.h2.string;
			else:
				data['title'] = ""
			data['creator'] = content2.find(id = 'viewauthor').find(attrs = {"itemprop" : "name"}).string;
			data['createdate'] = content2.find(attrs={"itemprop" : "datePublished"})["content"]
			data['description'] = content2.find(id = "description").text;
			data['url'] = URL_BASE + content2.find(id="viewimg").a["href"]
			data['keyword'] = []
			pointer = content2.find(id="viewtags")
			for k in pointer.span.find_all('a'):
				data['keyword'].append(k.text);
			pointer = pointer.next_sibling.next_sibling.next_sibling.next_sibling
			data['views'] = int(pointer.text.split(' ')[0])
			pointer = pointer.next_sibling.next_sibling.next_sibling.next_sibling
			data['good'] = int(pointer.text.split(' ')[0])
			pointer = pointer.next_sibling.next_sibling.next_sibling.next_sibling
			data['filesize'] = long(pointer.text.split(' ')[0])
			currentTime = datetime.datetime.utcnow()
			data['update_at'] = currentTime
			update_queries.append(UpdateOne({'_id':data['_id']}, {'$set': data, '$setOnInsert':{'created_at':currentTime}},True))
		except Exception as e:
			print "Failed to get data %s, Exception:" % url , e
			error.append({'Error url' :url, 'type':'get data', 'Exception': e})

	return update_queries
		


if __name__ == '__main__':
	db = getDB();
	if db is None:
		print "No db connected"
		exit

	#update MAX_PAGE
	MAX_PAGE = updatePage(1)

	from_page = 1
	to_page = MAX_PAGE
	if len(sys.argv) > 1:
		from_page = int(sys.argv[1])
	if len(sys.argv) > 2:
		to_page = int(sys.argv[2])

	for i in range(from_page, to_page + 1):
		if i > MAX_PAGE:
			print "Meet max page", MAX_PAGE
			break;
		insertDB(db, getData(i));
		print "Page", i, "Done"

	print "Error log:",error