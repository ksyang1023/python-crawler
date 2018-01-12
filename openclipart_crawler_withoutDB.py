from bs4 import BeautifulSoup
import requests
import datetime
import sys
from openclipart_crawler import * 

MAX_PAGE = 4168

error = []

if __name__ == '__main__':
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
		data = getData(i);
		print data;
		print "Page", i, "Done"

	print "Error log:",error