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

proxies = {
  "http": "http://54.76.53.211:3128",
  "https": "http://54.76.53.211:3128",
} 

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
	def UpdateShowList(self, showList):
		self.__shows = self.__GetData()
		for show in self.__shows:
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show[0])), False)
			if (match_index):
				shows[match_index]['sites']['crunchyroll'] = "http://www.crunchyroll.com" + show[1]
			else:
				show_obj = {'name': show[0], 'sites': {'crunchyroll': "http://www.crunchyroll.com" + show[1]}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		blob = requests.get('http://www.crunchyroll.com/videos/anime/alpha?group=all', proxies = proxies)
		print(blob.status_code)
		regex = '<a title=\"([^\"]*)\" token=\"shows-portraits\" itemprop=\"url\" href=\"([^\"]*)\"'
		return re.findall(regex, blob.text)
		
class Funimation(AnimeSource):
	def __init(self):
		self.__shows = []
	def UpdateShowList(self, showList):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show[1])), False)
			if (match_index):
				shows[match_index]['sites']['funimation'] = show[0]
			else:
				show_obj = {'name': show[1], 'sites': {'funimation': show[0]}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		blob = requests.get('http://www.funimation.com/videos/episodes' , proxies = proxies)
		regex = '<a class=\"fs16 bold\" href=\"([^\"]*)\">([^\"]*)</a>'
		return re.findall(regex, blob.text)
		
	
class Netflix(AnimeSource):
	def __init(self):
		self.__shows = []
	def UpdateShowList(self, showList):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			#print(show['show']['name'])
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show)), False)
			if (match_index):
				shows[match_index]['sites']['netflix'] = True
			else:
				show_obj = {'name': show, 'sites': {'netflix': True}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		blob = requests.get('http://animeonnetflix.com/anime-shows-on-netflix/', proxies = proxies)
		regex = "<span class=\"mg_overlay_tit\">([^\"]*) \([0-9-]*\)</span>"
		return re.findall(regex, blob.text)
		
class Daisuki(AnimeSource):
	def __init(self):
		self.__shows = []

	def UpdateShowList(self, showList):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			#print(show)
			url = "http://www.daisuki.net/anime/detail/" + show['ad_id']
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show['title'])), False)
			if (match_index):
				shows[match_index]['sites']['daisuki'] = url
			else:
				show_obj = {'name': show['title'], 'sites': {'daisuki': url}}
				showList.append(show_obj)

		return shows
	
	def __GetData(self):
		blob = requests.get('http://www.daisuki.net/fastAPI/anime/search/?' , proxies = proxies)
		#print(blob.text)
		return blob.json()['response']
		
class Viewster(AnimeSource):
	def __init(self):
		self.__shows = []
	def UpdateShowList(self, showList):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			#print(show)
			url = "https://www.viewster.com/serie/" + show['OriginId']
			if (type(show['Title']) is str):
				match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show['Title'])), False)
			if (match_index):
				shows[match_index]['sites']['viewster'] = url
			else:
				show_obj = {'name': show['Title'], 'sites': {'viewster': url}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		api_blob = requests.get('https://www.viewster.com/', proxies = proxies)
		api_token = api_blob.cookies['api_token']
		headers = {'Auth-token': parse.unquote(api_token)}
		anime_blob = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=1&genreId=58', headers = headers, proxies = proxies)
		return json.loads(anime_blob.text)['Items']
		
shows = []
sources = [Crunchyroll(), Funimation(), Daisuki(), Viewster()]
for source in sources:
	source.UpdateShowList(shows)
shows = sorted(shows, key = lambda show: show['name'].lower())
out_file = open('../public/data/uk.json', 'w')
json.dump(shows, out_file)
print('done')