import sys
sys.path.append("site-packages")
import requests
import cfscrape
import json
import re
import time
from abc import ABCMeta, abstractmethod
import string
from unidecode import unidecode
from urllib import parse
from datetime import datetime
import xml.etree.ElementTree as ET
import uuid
import random

import requests
import oauthlib.oauth1.rfc5849.signature as oauth

TRANS_TABLE = {ord(c): None for c in string.punctuation}

def compare(first, second):
	return unidecode(first.lower()).translate(TRANS_TABLE).replace('  ', ' ') == second

def getVRVSignature(key, secret, timestamp, nonce):
	headers={
		"Authorization": 'OAuth oauth_consumer_key="' + key + '",oauth_signature_method="HMAC-SHA1",oauth_timestamp="' + timestamp + '",oauth_nonce="' + nonce +'",oauth_version="1.0"'
	}
	params=oauth.collect_parameters(
		uri_query="",
		body=[],
		headers=headers,
		exclude_oauth_signature=True,
		with_realm=False
	)
	norm_params = oauth.normalize_parameters(params)
	base_string = oauth.construct_base_string(
		"GET", 
		"https://api.vrv.co/core/index", 
		norm_params
	)
	sig=oauth.sign_hmac_sha1(
		base_string,
		secret,
		''
	)
	return parse.quote(sig)


class AnimeSource:
	__metaclass__ = ABCMeta
	
	def __init__(self, titleMap, multiSeason, region, proxy):
		self.name = ""
		self.shows = []
		self.titleMap = titleMap
		self.multiSeason = multiSeason
		self.region = region
		self.proxy = proxy
	
	@abstractmethod
	def UpdateShowList(self, showList):
		pass
		
	@abstractmethod
	def GetData(self):
		pass

	def GetName(self):
		return self.name 
		
	def AddShow(self, showName, showUrl, showList):
		showNames = [showName]
		if (showName in self.titleMap):
			showNames[0] = self.titleMap[showName]
		if (self.name in self.titleMap):
			if (showNames[0] in self.titleMap[self.name]):
				if (self.titleMap[self.name][showNames[0]] == ""):
					return
				showNames[0] = self.titleMap[self.name][showNames[0]]
		if (self.name in self.multiSeason):
			if (showNames[0] in self.multiSeason[self.name]):
				showNames = showNames + self.multiSeason[self.name][showNames[0]]
		for name in showNames:
			translated_name = unidecode(name.lower()).translate(TRANS_TABLE).replace('  ', ' ')
			if (translated_name in showList):
				showList[translated_name]['sites'][self.name] = showUrl
			else:
				show_obj = {'name': name, 'sites': {self.name: showUrl}}
				showList[translated_name] = show_obj
		
class Crunchyroll(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "crunchyroll"
		
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[0].strip())
			showUrl = "http://www.crunchyroll.com" + show[1]
			AnimeSource.AddShow(self, showName, showUrl, showList)
			
	def GetData(self):
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		crSession = cfscrape.create_scraper()
		params = {
			"formname": "RpcApiUser_Login",
			"failurl": "http://www.crunchyroll.com/login",
			"name": credentials['crunchyroll']['username'], 
			"password": credentials['crunchyroll']['password']
		}
		crSession.get('https://www.crunchyroll.com/login', params=params, proxies = self.proxy)
		crSession.post('https://www.crunchyroll.com/?a=formhandler', params=params, proxies = self.proxy)
		blob = crSession.get('http://www.crunchyroll.com/videos/anime/alpha?group=all', proxies = self.proxy)
		regex = '<a title=\"([^\"]*)\" token=\"shows-portraits\" itemprop=\"url\" href=\"([^\"]*)\"'
		return re.findall(regex, blob.text)

class VRVCrunchyroll(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "vrv-crunchyroll"
		
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['title'].strip())
			showUrl = "https://vrv.co/" + ('series/' if show['type'] == 'series' else 'watch/') + show['id']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		key = credentials["vrv"]["key"]
		secret = credentials["vrv"]["secret"]
		timestamp = str(int(time.time()))
		nonce = uuid.uuid4().hex
		vrvSig = getVRVSignature(key, secret, timestamp, nonce)
		headers={
			"Authorization": 'OAuth oauth_consumer_key="' + key + '",oauth_signature_method="HMAC-SHA1",oauth_timestamp="' + timestamp + '",oauth_nonce="' + nonce +'",oauth_version="1.0",oauth_signature='+ vrvSig
		}
		authBlob = requests.get("https://api.vrv.co/core/index", headers = headers, proxies = self.proxy)
		authPolicies = json.loads(authBlob.text)['signing_policies']
		policy = authPolicies[0]["value"]
		signature = authPolicies[1]["value"]
		keyPairId = authPolicies[2]["value"]
		dataBlob = requests.get("https://api.vrv.co/disc/public/v1/US/M2/-/-/browse?channel_id=crunchyroll&n=10000&sort_by=alphabetical&start=0&Policy=" + policy + "&Signature=" + signature + "&Key-Pair-Id=" + keyPairId)
		return json.loads(dataBlob.text)['items']

class VRVFunimation(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "vrv-funimation"
		
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['title'].strip())
			showUrl = "https://vrv.co/" + ('series/' if show['type'] == 'series' else 'watch/') + show['id']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		key = credentials["vrv"]["key"]
		secret = credentials["vrv"]["secret"]
		timestamp = str(int(time.time()))
		nonce = uuid.uuid4().hex
		vrvSig = getVRVSignature(key, secret, timestamp, nonce)
		headers={
			"Authorization": 'OAuth oauth_consumer_key="' + key + '",oauth_signature_method="HMAC-SHA1",oauth_timestamp="' + timestamp + '",oauth_nonce="' + nonce +'",oauth_version="1.0",oauth_signature='+ vrvSig
		}
		authBlob = requests.get("https://api.vrv.co/core/index", headers = headers, proxies = self.proxy)
		authPolicies = json.loads(authBlob.text)['signing_policies']
		policy = authPolicies[0]["value"]
		signature = authPolicies[1]["value"]
		keyPairId = authPolicies[2]["value"]
		dataBlob = requests.get("https://api.vrv.co/disc/public/v1/US/M2/-/-/browse?channel_id=funimation&n=10000&sort_by=alphabetical&start=0&Policy=" + policy + "&Signature=" + signature + "&Key-Pair-Id=" + keyPairId)
		return json.loads(dataBlob.text)['items']
		
class FunimationOld(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "funimation-old"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[1].strip())
			showUrl = show[0]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		blob = requests.get('http://www.funimation.com/videos/episodes', proxies = self.proxy)
		regex = '<a class=\"fs16 bold\" href=\"([^\"]*)\">([^\"]*)</a>'
		return re.findall(regex, blob.text)
		
class Funimation(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "funimation"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['title'].strip())
			showUrl = 'http://www.funimation.com/shows/' + show['id']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		blob = requests.get('https://api-funimation.dadcdigital.com/xml/longlist/content/page/?id=shows&sort=&title=All+Shows&sort_direction=DESC&role=g&itemThemes=dateAddedShow&limit=500&offset=0&territory=' + self.region, proxies = self.proxy)
		item_list = ET.fromstring(blob.text).iterfind('item')
		return [{'title': show.find('title').text, 'id': show.find('id').text} for show in item_list]
		results = []
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		session = requests.Session()
		login_params = {
			'username': credentials['funimation']['username'], 
			'password': credentials['funimation']['password'], 
		}
		login_blob = session.post('https://prod-api-funimationnow.dadcdigital.com/api/auth/login', params = login_params, proxies = self.proxy)
		search_blob = session.get('https://prod-api-funimationnow.dadcdigital.com/api/source/funimation/search/auto?unique=true&limit=100&q=', proxies = self.proxy)
		num_items = int(json.loads(search_blob.text)["count"])
		num_pages = (num_items // 100) + 1
		for curIndex in range(1, num_pages + 1):
			offset = 100 * (curIndex - 1)
			page_blob = session.get('https://prod-api-funimationnow.dadcdigital.com/api/source/funimation/search/auto?unique=true&limit=100&q=&offset=' + str(offset), proxies = self.proxy)
			page_item = json.loads(page_blob.text)["items"]["hits"]
			results += page_item
		return results
		
class Hulu(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "hulu"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')

		for show in self.shows:
			showName = unidecode(show[1].strip())
			showUrl = show[0]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		url = 'https://www.hulu.com/start/more_content?channel=anime&video_type=all&sort=alpha&is_current=0&closed_captioned=0&has_hd=0&page='
		first_page = requests.get(url + '1#')
		num_pages_regex = "total_pages=\"([\d']*)\""
		num_pages = int(re.findall(num_pages_regex, first_page.text)[0])
		results = []
		for curIndex in range(1, num_pages):
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
			}
			blob = requests.get(url + str(curIndex) + '#', headers = headers, proxies = self.proxy)
			regex = '<a href=\"([^\"]*)\".*\);\"><img alt=\"([^\"]*)\"'
			results += re.findall(regex, blob.text)
		return results
		
class Netflix(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "netflix"
		self.countryCodes = {
			'us': '78',
			'uk': '46',
			'ca': '33',
			'au': '23'
		}

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[1].strip())
			showUrl = "http://www.netflix.com/title/" + show[0]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		headers = {
			"X-Mashape-Key": credentials['mashape'],
			"Accept": "application/json"
		}
		hasMoreResults = True
		allItems = []
		curPage = 1
		while (hasMoreResults):
			dataBlob = requests.get("https://unogs-unogs-v1.p.rapidapi.com/api.cgi?q=-!1900,3000-!0,5-!0,10-!10695%2C11146%2C2653%2C2729%2C3063%2C413820%2C452%2C6721%2C7424%2C9302-!Any-!Any-!Any-!gt0&t=ns&st=adv&ob=Relevance&sa=and&cl=" + self.countryCodes[self.region] + "&p=" + str(curPage), headers = headers)
			newItems = json.loads(dataBlob.text)["ITEMS"]
			allItems += newItems
			curPage += 1
			if (len(newItems) == 0):
				hasMoreResults = False
		return allItems
		
		
class Daisuki(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "daisuki"
		self.countryCodes = {
			'us': 'us',
			'uk': 'gb',
			'ca': 'ca',
			'au': 'au'
		}

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.shows:
			showName = unidecode(show['title'].strip())
			showUrl = "http://www.daisuki.net/anime/detail/" + show['ad_id']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		blob = requests.get('http://www.daisuki.net/bin/wcm/searchAnimeAPI?api=anime_list&searchOptions=&currentPath=%2Fcontent%2Fdaisuki%2F' + self.countryCodes[self.region] + '%2Fen', proxies = self.proxy)
		return blob.json()['response']
		
class Viewster(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "viewster"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['Title'].strip())
			showUrl = "https://www.viewster.com/serie/" + show['OriginId']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		api_blob = requests.get('https://www.viewster.com/', proxies = self.proxy)
		api_token = api_blob.cookies['api_token']
		headers = {'Auth-token': parse.unquote(api_token)}
		anime_blob = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=1&genreId=58', headers = headers, proxies = self.proxy)
		anime_blob2 = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=2&genreId=58', headers = headers, proxies = self.proxy)
		simul_blob = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=1&genreId=67', headers = headers, proxies = self.proxy)
		try: 
			simul_items = json.loads(simul_blob.text)['Items']
			return json.loads(anime_blob.text)['Items'] + json.loads(anime_blob2.text)['Items'] + simul_items
		except:
			return json.loads(anime_blob.text)['Items'] + json.loads(anime_blob2.text)['Items']
		
class AnimeLab(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "animelab"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['name'].strip())
			showUrl = "https://www.animelab.com/shows/" + show['slug']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		results = []
		for curIndex in range(0, 5):
			blob = requests.get('https://www.animelab.com/api/shows/all?limit=100&page=' + str(curIndex), proxies = self.proxy)
			results += json.loads(blob.text)['list']
		return results
		
class Animax(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "animax"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			#print(show)
			showName = unidecode(show[1].strip())
			showUrl = "https://www.animaxtv.co.uk/" + show[0]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		blob = requests.get('http://www.animaxtv.co.uk/programs', proxies = self.proxy)
		regex1 = '<optgroup label=\"Shows &amp; Movies\">(.*)</optgroup></select>'
		regex2 = '<option value=\"([^\"]*)\">([^\"]*)</option>'
		data1 = re.findall(regex1, blob.text)[0]
		return re.findall(regex2, data1)
		
class Hanabee(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "hanabee"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		for show in self.shows:
			#print(show)
			showName = unidecode(show[1].strip())
			showUrl = "http://hanabee.tv" + show[0]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		results = []
		for curIndex in range(0, 5):
			blob = requests.get('http://hanabee.tv/shows/?vod-filter-button=on&start=' + str(curIndex * 10) , proxies = self.proxy)
			regex = '<h3><a href=\"([^\"]*)\" >([^\"]*)</a></h3>'
			results += re.findall(regex, blob.text)
		return results
		
class AnimeNetwork(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "animenetwork"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[0].strip().replace('&#39;', '\''))
			showUrl = "http://www.theanimenetwork.com" + show[1]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		results = []
		pages = ['0'] + list(string.ascii_uppercase)
		for letter in pages:
			blob = requests.get('http://www.theanimenetwork.com/Watch-Anime/Alphabet/' + letter, proxies = self.proxy)
			regex = '<h3 class=\"small hidden-sm hidden-xs\">([^\"]*)</h3>[\n\s]*<a href=\"([^\"]*)\">'
			print(letter)
			results += re.findall(regex, blob.text, re.M)
		return results

class TubiTV(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "tubitv"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = self.shows[show]['title']
			showTypes = {'v': 'video', 's': 'series'}
			showUrl = 'http://tubitv.com/' + showTypes[self.shows[show]['type']] + '/' + str(int(show))
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		blob = requests.get('http://tubitv.com/oz/containers/anime/content?cursor=0&limit=1000', proxies = self.proxy)
		return json.loads(blob.text)['contents']

class AnimeStrike(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "animestrike"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[0].strip())
			showUrl = show[1]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		results = []
		for curIndex in range(1, 15):
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
			}
			blob = requests.get('https://www.amazon.com/s/ref=sr_ex_n_1?rh=n%3A2858778011%2Cp_n_subscription_id%3Asaikindo&bbn=2858778011&ie=UTF8&qid=1512620557&page=' + str(curIndex) , headers = headers, proxies = self.proxy)
			regex = '<a class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal" title="([^\"]*)" href="([^\"]*)"'
			results += re.findall(regex, blob.text)
		return results

class HiDive(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "hidive"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[1].strip().replace('&#39;', '\''))
			showUrl = show[0]
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		results = []
		blob_tv = requests.get('https://www.hidive.com/tv', proxies = self.proxy)
		regex_tv = '<div class=\"player\">[\n\s]*<a href=\"([^\"]*)\"[\s\S]*?<h3 title=\"([^\"]*)\">'
		results += re.findall(regex_tv, blob_tv.text, re.M)
		blob_movies = requests.get('https://www.hidive.com/movies', proxies = self.proxy)
		regex_movies = '<div class=\"player\">[\n\s]*<a href=\"([^\"]*)\"[\s\S]*?<h3 title=\"([^\"]*)\">'
		results += re.findall(regex_movies, blob_movies.text, re.M)
		return results

class VRVHidive(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "vrv-hidive"
		
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['title'].strip())
			showUrl = "https://vrv.co/" + ('series/' if show['type'] == 'series' else 'watch/') + show['id']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		key = credentials["vrv"]["key"]
		secret = credentials["vrv"]["secret"]
		timestamp = str(int(time.time()))
		nonce = uuid.uuid4().hex
		vrvSig = getVRVSignature(key, secret, timestamp, nonce)
		headers={
			"Authorization": 'OAuth oauth_consumer_key="' + key + '",oauth_signature_method="HMAC-SHA1",oauth_timestamp="' + timestamp + '",oauth_nonce="' + nonce +'",oauth_version="1.0",oauth_signature='+ vrvSig
		}
		authBlob = requests.get("https://api.vrv.co/core/index", headers = headers, proxies = self.proxy)
		authPolicies = json.loads(authBlob.text)['signing_policies']
		policy = authPolicies[0]["value"]
		signature = authPolicies[1]["value"]
		keyPairId = authPolicies[2]["value"]
		dataBlob = requests.get("https://api.vrv.co/disc/public/v1/US/M2/-/-/browse?channel_id=hidive&n=10000&sort_by=alphabetical&start=0&Policy=" + policy + "&Signature=" + signature + "&Key-Pair-Id=" + keyPairId)
		return json.loads(dataBlob.text)['items']

class YahooView(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "yahoo"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['title'].strip().replace('&#39;', '\''))
			showUrl = "https://view.yahoo.com/show/" + show['id']
			AnimeSource.AddShow(self, showName, showUrl, showList)

	def GetData(self):
		blob = requests.get('https://view.yahoo.com/browse/tv/genre/anime/shows', proxies = self.proxy)
		regex = '\"seriesListItems\":(.*)},\"StreamStore\"'
		resultsJson = re.findall(regex, blob.text)[0]
		results = json.loads(resultsJson)
		return results

class AmazonPrime(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "amazon"

	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if not self.shows:
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[0].strip())
			showUrl = show[1]
			AnimeSource.AddShow(self, showName, showUrl, showList)
			if (self.region == 'us'):
				showName = unidecode(show[1].strip())
				showUrl = 'https://www.amazon.com/' + show[0]
				AnimeSource.AddShow(self, showName, showUrl, showList)
			else:
				showName = unidecode(show[1].strip())
				showUrl = 'https://www.amazon.co.uk/' + show[0]
				AnimeSource.AddShow(self, showName, showUrl, showList)
	def GetData(self):
		urls = {
			'us': 'https://www.amazon.com/s?k=prime+anime&i=instant-video&bbn=2858778011&rh=n%3A2858778011%2Cp_n_ways_to_watch%3A12007865011%2Cp_n_entity_type%3A14069184011%7C14069185011&dc&qid=1556179818&rnid=14069183011&ref=sr_pg_4&page=',
			'uk': 'https://www.amazon.co.uk/s?k=anime&i=prime-instant-video&bbn=3280626031&rh=p_n_entity_type%3A9739952031%7C9739955031&lo=list&dc&qid=1556040360&rnid=9739949031&ref=sr_pg_1&page='
		}
		regexes = {
			'us': '<a class="a-link-normal a-text-normal" href="([^\"]*)">[\s]*<span class="a-size-medium a-color-base a-text-normal">([^\"]*)</span>',
			'uk': '<a class="a-link-normal a-text-normal" href="([^\"]*)">[\s]*<span class="a-size-medium a-color-base a-text-normal">([^\"]*)</span>'
		}
		results = []
		for curIndex in range(1, 25):
			stillNeedPage = True
			tries = 0
			while (stillNeedPage and tries <= 10):
				print(curIndex)
				allUA = [
					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
					"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"
				]
				headers = {
					'User-Agent': random.sample(allUA, 1)[0]
				}
				blob = requests.get(urls[self.region] + str(curIndex) , headers = headers, proxies = self.proxy)
				stillNeedPage = ("Robot Check" in blob.text)
				tries+=1
				if (tries > 10):
					sys.exit("couldn't get page " + str(curIndex) + " for amazon")
			regex = regexes[self.region]
			results += re.findall(regex, blob.text)
		return results
