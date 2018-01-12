import requests
import json
from bs4 import BeautifulSoup


#freesound account imformation
ACCOUNT="crawlertest"
PASSWORD="hello"
CLIENT_ID = "9ordW5TB0rv7FUZmpeRD"
CLIENT_SECRET = "qULfofteJJ1ry7OmrxwBZILkMmDS4oSm8WJL2UCc"

#return url fro getting access token
def getAccessTokenURL():
	return 'https://freesound.org/apiv2/oauth2/authorize/?client_id=%s&response_type=code&state=xyz' % CLIENT_ID


#get access token with account, password, client id, and client secrete from freesound.org
def getAccessToken():
	try:
		res = requests.Session()

		#get csfr token
		response = res.get('https://freesound.org/apiv2/login/')
		soup = BeautifulSoup(response.text, "lxml");
		token = soup.body.find('input', {'name': 'csrfmiddlewaretoken'})['value'];
		if token is None:
			raise Exception("Can't get csfr token")
		payload={'username':ACCOUNT, 'password':PASSWORD, 'csrfmiddlewaretoken':token}

		#build session
		res.headers.update({"Referer" : "https://freesound.org/apiv2/login/"})
		response = res.post('https://freesound.org/apiv2/login/', data = payload)

		#get access token
		response = res.get(getAccessTokenURL())
		soup = BeautifulSoup(response.text, "lxml");

		#Have to authorize while asking token for the first time
		if "requesting" in soup.find('div',{'class':'container'}).p.text:
			token = soup.body.find('input', {'name': 'csrfmiddlewaretoken'})['value'];
			payload = {'csrfmiddlewaretoken': token, 'scope': 'read write', 'redirect_uri': 'https://freesound.org/home/app_permissions/permission_granted/', 'response_type': 'code','client_id': CLIENT_ID, 'allow': 'Authorize!'}
			res.headers.update({"Referer" : getAccessTokenURL()})
			response = res.post(AUTORIZE_URL, data = payload)
			soup = BeautifulSoup(response.text, "lxml");

		authorization_code = soup.find('div',{'class':'container'}).div.text
		payload = {'client_id':CLIENT_ID, 'CLIENT_SECRET': CLIENT_SECRET, 'grant_type':'authorization_code', 'code':authorization_code}
		response = res.post('https://freesound.org/apiv2/oauth2/access_token/', data= payload)
		access_token = json.loads(response.text)['access_token']
		return access_token
	except Exception as e:
		print "Get access token failed:", e
		return None