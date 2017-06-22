import sys
sys.path.append("site-packages")
import requests
import json
import re
from abc import ABCMeta, abstractmethod
import string
from unidecode import unidecode
from urllib import parse
from datetime import datetime
import xml.etree.ElementTree as ET

transtable = {ord(c): None for c in string.punctuation}
def compare(first, second):
	return unidecode(first.lower()).translate(transtable).replace('  ', ' ') == unidecode(second.lower()).translate(transtable).replace('  ', ' ')

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
				showNames[0] = self.titleMap[self.name][showNames[0]]
		if (self.name in self.multiSeason):
			if (showNames[0] in self.multiSeason[self.name]):
				showNames = showNames + self.multiSeason[self.name][showNames[0]]
				#print(showNames)
		for name in showNames:
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], name)), False)
			if (type(match_index) == int):
				showList[match_index]['sites'][self.name] = showUrl
			else:
				show_obj = {'name': name, 'sites': {self.name: showUrl}}
				showList.append(show_obj)
		
class Crunchyroll(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "crunchyroll"
		
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if (len(self.shows) == 0):
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[0].strip())
			showUrl = "http://www.crunchyroll.com" + show[1]
			AnimeSource.AddShow(self, showName, showUrl, showList)
	def GetData(self):
		with open('credentials.json') as creds_file:
			credentials = json.load(creds_file)
		crSession = requests.Session()
		params = {
			"formname": "RpcApiUser_Login",
			"failurl": "http://www.crunchyroll.com/login",
			"name": credentials['crunchyroll']['username'], 
			"password": credentials['crunchyroll']['password']
		}
		crSession.post('https://www.crunchyroll.com/?a=formhandler', params=params, proxies = self.proxy)
		blob = crSession.get('http://www.crunchyroll.com/videos/anime/alpha?group=all', proxies = self.proxy)
		regex = '<a title=\"([^\"]*)\" token=\"shows-portraits\" itemprop=\"url\" href=\"([^\"]*)\"'
		return re.findall(regex, blob.text)
		
class FunimationOld(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "funimation-old"
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if (len(self.shows) == 0):
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
		if (len(self.shows) == 0):
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['title'].strip())
			showUrl = 'http://www.funimation.com/shows/' + show['id']
			AnimeSource.AddShow(self, showName, showUrl, showList)
	def GetData(self):
		results = []
		blob = requests.get('https://api-funimation.dadcdigital.com/xml/longlist/content/page/?id=shows&sort=&title=All+Shows&sort_direction=DESC&role=g&itemThemes=dateAddedShow&limit=500&offset=0&territory=' + self.region, proxies = self.proxy)
		list = ET.fromstring(blob.text)
		for show in list.iterfind('item'):
			results.append({'title': show.find('title').text, 'id': show.find('id').text})
		return results
		
class Hulu(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "hulu"
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if (len(self.shows) == 0):
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['show']['name'].strip())
			showUrl = 'http://www.hulu.com/' + show['show']['canonical_name']
			AnimeSource.AddShow(self, showName, showUrl, showList)
	def GetData(self):
		oauth_blob = requests.get('http://www.hulu.com/tv/genres/anime')
		oauth_regex = "w.API_DONUT = '([^']*)';"
		oauth_key = re.findall(oauth_regex, oauth_blob.text)[0]
		movies_blob = requests.get('http://www.hulu.com/mozart/v1.h2o/movies?exclude_hulu_content=1&genre=anime&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=0&region=us&locale=en&language=en&access_token=' + oauth_key)
		anime_blob = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=anime&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=0&region=us&locale=en&language=en&access_token=' + oauth_key)
		anime_blob_2 = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=anime&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=500&region=us&locale=en&language=en&access_token=' + oauth_key)
		animation_blob = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=animation&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=0&region=us&locale=en&language=en&access_token=' + oauth_key)
		animation_list = json.loads(animation_blob.text)['data']
		animation_list = [x for x in animation_list if x['show']['genre'] == "Anime"]
		anime_list = json.loads(anime_blob.text)['data'] + json.loads(anime_blob_2.text)['data'] + json.loads(movies_blob.text)['data']
		return anime_list + animation_list
		
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
		if (len(self.shows) == 0):
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
		dataBlob = requests.get("https://unogs-unogs-v1.p.mashape.com/api.cgi?q=-!1900,3000-!0,5-!0,10-!10695%2C11146%2C2653%2C2729%2C3063%2C413820%2C452%2C6721%2C7424%2C9302-!Any-!Any-!Any-!gt0&t=ns&st=adv&ob=Relevance&p=1&sa=and&cl=" + self.countryCodes[self.region], headers = headers)
		return json.loads(dataBlob.text)["ITEMS"]
		
		
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
		if (len(self.shows) == 0):
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
		if (len(self.shows) == 0):
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
		if (len(self.shows) == 0):
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show['name'].strip())
			showUrl = "https://www.animelab.com/shows/" + show['slug']
			AnimeSource.AddShow(self, showName, showUrl, showList)
	def GetData(self):
		shows_blob0 = requests.get('https://www.animelab.com/api/shows/all?limit=100&page=0', proxies = self.proxy)
		shows_blob1 = requests.get('https://www.animelab.com/api/shows/all?limit=100&page=1', proxies = self.proxy)
		shows_blob2 = requests.get('https://www.animelab.com/api/shows/all?limit=100&page=2', proxies = self.proxy)
		return json.loads(shows_blob0.text)['list'] + json.loads(shows_blob1.text)['list'] + json.loads(shows_blob2.text)['list'] 
		
class Animax(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "animax"
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if (len(self.shows) == 0):
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
		if (len(self.shows) == 0):
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
		if (len(self.shows) == 0):
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
		if (len(self.shows) == 0):
			sys.exit('0 shows found for ' + self.name + ', aborting')
		for show in self.shows:
			showName = unidecode(show[0].strip())
			showUrl = show[1]
			AnimeSource.AddShow(self, showName, showUrl, showList)
	def GetData(self):
		results = []
		for curIndex in range(1, 10):
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
			}
			blob = requests.get('https://www.amazon.com/s/ref=sr_pg_2?fst=as%3Aoff&rh=n%3A2858778011%2Cp_n_subscription_id%3A16182082011&bbn=2858778011&ie=UTF8&page=' + str(curIndex) , headers = headers, proxies = self.proxy)
			regex = '<a class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal" title="([^\"]*)" href="([^\"]*)"'
			results += re.findall(regex, blob.text)
		return results

class HiDive(AnimeSource):
	def __init__(self, titleMap, multiSeason, region = 'us', proxy = {}):
		AnimeSource.__init__(self, titleMap, multiSeason, region, proxy)
		self.name = "hidive"
	def UpdateShowList(self, showList):
		self.shows = self.GetData()
		if (len(self.shows) == 0):
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