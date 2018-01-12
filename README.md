# python-crawler
Python crawlers for freesound.org and openclipart.org

### Files
* **mongodb_info** 				- variables needed to communicate with mongoDB
* **freesound_account_info**  - variables needed for freesound.org Oauth 2.0 validation
* **freesound_crawler** 			- crawling data from freesound.org, then insert them into mongoDB
* **openclipart_crawler** 		- getting access token with an existed account and crawling data from openclipart.org, then insert them into 								mongoDB
* **freesound_crawler_withouDB**  - crawling data from freesound.org and pirnting them out
* **openclipart_crawler_withouDB**- crawling data from openclipart.org and pirnting them out

### Usage
```
  python freesound_crawler.py [from_page] [to_page]
  python freesound_crawler_withoutDB.py [from_page] [to_page]
  python openclipart_crawler.py [from_page] [to_page]
  python openclipart_crawle_withoutDBr.py [from_page] [to_page]
```
* from_page and to_page are optional, would crawl the whole website if they are empty
* APIs from freesound.org are limited to send 2000 requests a day from a client ID

### Environment:
  Python 2.7

### Dependencies: 
  BeautifulSoup, requests, pymongo, json
