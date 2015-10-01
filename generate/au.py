import sys
sys.path.append("site-packages")
import requests
import json
import re
from abc import ABCMeta, abstractmethod
import string
from unidecode import unidecode
from urllib import parse
from azure.storage.blob import BlobService

transtable = {ord(c): None for c in string.punctuation}

def compare(first, second):
	return unidecode(first.lower()).translate(transtable).replace('  ', ' ') == unidecode(second.lower()).translate(transtable).replace('  ', ' ')

class AnimeSource(object):
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def UpdateShowList(self, showList):
		pass
		
class Crunchyroll(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Crunchyroll"
	def UpdateShowList(self, showList, titleMap, proxy):
		self.__shows = self.__GetData(proxy)
		for show in self.__shows:
			showName = unidecode(show[0])
			showUrl = "http://www.crunchyroll.com" + show[1]
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['crunchyroll'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'crunchyroll': showUrl}}
				showList.append(show_obj)
		return shows
	def __GetData(self, dataProxy):
		blob = requests.get('http://www.crunchyroll.com/videos/anime/alpha?group=all', proxies = dataProxy)
		regex = '<a title=\"([^\"]*)\" token=\"shows-portraits\" itemprop=\"url\" href=\"([^\"]*)\"'
		return re.findall(regex, blob.text)
		
class Netflix(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Netflix"
	def UpdateShowList(self, showList, titleMap, proxy):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = unidecode(show[1].strip())
			showUrl = "http://www.netflix.com/title/" + show[0]
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['netflix'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'netflix': showUrl}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		unogsSession = requests.Session()
		getCgiUrlBlob = unogsSession.get('http://unogs.com/search')
		getCgiUrlRegex = 'var cgiurl=\'([^\&"]*)\';'
		
		cgiUrl = re.findall(getCgiUrlRegex, getCgiUrlBlob.text)[0]
		headers = {
			'Referer': 'http://unogs.com/search/?q=-!1900,2016-!0,5-!0,10-!7424-!Any-!Any-!Any&cl=23,&st=adv&ob=Relevance',
			'Accept': 'application/json, text/javascript, */*; q=0.01'
		}
		dataBlob = unogsSession.get('http://unogs.com' + cgiUrl + '&q=-!1900,2016-!0,5-!0,10-!7424-!Any-!Any-!Any&t=ns&cl=23,&st=adv&ob=Relevance', headers = headers)
		return json.loads(dataBlob.text)["ITEMS"]
		
class Daisuki(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Daisuki"
	def UpdateShowList(self, showList, titleMap, proxy):
		self.__shows = self.__GetData(proxy)
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = unidecode(show['title'])
			showUrl = "http://www.daisuki.net/anime/detail/" + show['ad_id']
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['daisuki'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'daisuki': showUrl}}
				showList.append(show_obj)

		return shows
	
	def __GetData(self, dataProxy):
		blob = requests.get('http://www.daisuki.net/fastAPI/anime/search/?', proxies = dataProxy)
		return blob.json()['response']
		
class Viewster(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Viewster"
	def UpdateShowList(self, showList, titleMap, proxy):
		self.__shows = self.__GetData(proxy)
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = unidecode(show['Title'].strip())
			showUrl = "https://www.viewster.com/serie/" + show['OriginId']
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['viewster'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'viewster': showUrl}}
				showList.append(show_obj)
		return shows
	def __GetData(self, dataProxy):
		api_blob = requests.get('https://www.viewster.com/', proxies = dataProxy)
		api_token = api_blob.cookies['api_token']
		headers = {'Auth-token': parse.unquote(api_token)}
		anime_blob = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=1&genreId=58', headers = headers, proxies = dataProxy)
		anime_blob2 = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=2&genreId=58', headers = headers, proxies = dataProxy)
		return json.loads(anime_blob.text)['Items'] + json.loads(anime_blob2.text)['Items']
		
class AnimeLab(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "AnimeLab"
	def UpdateShowList(self, showList, titleMap, proxy):
		self.__shows = self.__GetData(proxy)
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = unidecode(show['name'].strip())
			showUrl = "https://www.animelab.com/shows/first/" + show['slug']
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['animelab'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'animelab': showUrl}}
				showList.append(show_obj)
		return shows
	def __GetData(self, dataProxy):
		shows_blob1 = requests.get('https://www.animelab.com/api/shows/all?limit=100&page=0', proxies = dataProxy)
		shows_blob2 = requests.get('https://www.animelab.com/api/shows/all?limit=100&page=1', proxies = dataProxy)
		#print(shows_blob1.text)
		return json.loads(shows_blob1.text)['list'] + json.loads(shows_blob2.text)['list']
		
shows = []
sources = [Crunchyroll(), Netflix(), Daisuki(), Viewster(), AnimeLab()]
#sources = [AnimeLab()]
with open('title-map.json') as titlemap_file:
	titlemap = json.load(titlemap_file)
with open('azure.json') as azure_file:
	azure_storage = json.load(azure_file)
azure_blob = BlobService(account_name=azure_storage['account'], account_key=azure_storage['key'])
with open('proxies.json') as proxies_file:
	proxy_data = json.load(proxies_file)
	proxy = proxy_data['au']
for source in sources:
	source.UpdateShowList(shows, titlemap, proxy)
	print('number of shows:' + str(len(shows)))
with open('alternates.json') as alternates_file:
	alternates = json.load(alternates_file)
for alternate in alternates:
	match_index = next((i for i, x in enumerate(shows) if compare(x['name'], alternate)), False)
	if (match_index):
		shows[match_index]['alt'] = alternates[alternate]
shows = sorted(shows, key = lambda show: show['name'].lower())
out_file = open('../public/data/au.json', 'w')
json.dump(shows, out_file)
out_file.close()
azure_blob.put_block_blob_from_path(
	'assets',
	'au.json',
	'../public/data/au.json',
	x_ms_blob_content_type='application/json'
)
print('done')