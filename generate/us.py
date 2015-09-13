import sys
sys.path.append("site-packages")
import requests
import json
import re
from abc import ABCMeta, abstractmethod
import string
from unidecode import unidecode
from urllib import parse

transtable = {ord(c): None for c in string.punctuation}
def compare(first, second):
	return unidecode(first.lower()).translate(transtable).replace('  ', ' ') == unidecode(second.lower()).translate(transtable).replace('  ', ' ')


class AnimeSource(object):
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def UpdateShowList(self, showList):
		pass
	
	def GetName(self):
		return self.__name 
		
class Crunchyroll(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Crunchyroll"
	def UpdateShowList(self, showList, titleMap):
		self.__shows = self.__GetData()
		for show in self.__shows:
			showName = show[0]
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
	def __GetData(self):
		blob = requests.get('http://www.crunchyroll.com/videos/anime/alpha?group=all')
		regex = '<a title=\"([^\"]*)\" token=\"shows-portraits\" itemprop=\"url\" href=\"([^\"]*)\"'
		return re.findall(regex, blob.text)
		
class Funimation(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Funimation"
	def UpdateShowList(self, showList, titleMap):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = show[1]
			showUrl = show[0]
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['funimation'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'funimation': showUrl}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		blob = requests.get('http://www.funimation.com/videos/episodes')
		regex = '<a class=\"fs16 bold\" href=\"([^\"]*)\">([^\"]*)</a>'
		return re.findall(regex, blob.text)
		
class Hulu(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Hulu"
	def UpdateShowList(self, showList, titleMap):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = show['show']['name']
			showUrl = 'http://www.hulu.com/' + show['show']['canonical_name']
			if (showName in titleMap):
				showName = titleMap[showName]
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], showName)), False)
			if (match_index):
				shows[match_index]['sites']['hulu'] = showUrl
			else:
				show_obj = {'name': showName, 'sites': {'hulu': showUrl}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		oauth_blob = requests.get('http://www.hulu.com/tv/genres/anime')
		oauth_regex = "w.API_DONUT = '([^']*)';"
		oauth_key = re.findall(oauth_regex, oauth_blob.text)[0]
		anime_blob = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=anime&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=0&region=us&locale=en&language=en&access_token=' + oauth_key)
		anime_blob_2 = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=anime&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=500&region=us&locale=en&language=en&access_token=' + oauth_key)
		animation_blob = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=animation&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=0&region=us&locale=en&language=en&access_token=' + oauth_key)
		animation_list = json.loads(animation_blob.text)['data']
		#print(animation_list)
		animation_list = [x for x in animation_list if x['show']['genre'] == "Anime"]
		anime_list = json.loads(anime_blob.text)['data'] + json.loads(anime_blob_2.text)['data']
		return anime_list + animation_list
		
class Netflix(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Netflix"
	def UpdateShowList(self, showList, titleMap):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = show[1].strip()
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
			'Referer': 'http://unogs.com/search/?q=-!1900,2016-!0,5-!0,10-!7424-!Any-!Any-!Any&cl=78,&st=adv&ob=Relevance',
			'Accept': 'application/json, text/javascript, */*; q=0.01'
		}
		dataBlob = unogsSession.get('http://unogs.com' + cgiUrl + '&q=-!1900,2016-!0,5-!0,10-!7424-!Any-!Any-!Any&t=ns&cl=78,&st=adv&ob=Relevance', headers = headers)
		return json.loads(dataBlob.text)["ITEMS"]
		
		
class Daisuki(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Daisuki"
	def UpdateShowList(self, showList, titleMap):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = show['title']
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
	
	def __GetData(self):
		blob = requests.get('http://www.daisuki.net/fastAPI/anime/search/?')
		return blob.json()['response']
		
class Viewster(AnimeSource):
	def __init(self):
		self.__shows = []
		self.__name = "Viewster"
	def UpdateShowList(self, showList, titleMap):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			showName = show['Title']
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
	def __GetData(self):
		api_blob = requests.get('https://www.viewster.com/')
		api_token = api_blob.cookies['api_token']
		headers = {'Auth-token': parse.unquote(api_token)}
		anime_blob = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=1&genreId=58', headers = headers)
		return json.loads(anime_blob.text)['Items']
		
shows = []
sources = [Crunchyroll(), Funimation(), Hulu(), Netflix(), Daisuki(), Viewster()]
with open('title-map.json') as titlemap_file:
	titlemap = json.load(titlemap_file)
for source in sources:
	source.UpdateShowList(shows, titlemap)
	print('200')
shows = sorted(shows, key = lambda show: show['name'].lower())
out_file = open('../public/data/us.json', 'w')
json.dump(shows, out_file)
print('done')