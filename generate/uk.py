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
  "http": "http://128.199.179.154:80",
  "https": "http://128.199.179.154:80",
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
			#print(show)
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show[1].strip())), False)
			if (match_index):
				shows[match_index]['sites']['netflix'] = "http://www.netflix.com/title/" + show[0]
			else:
				show_obj = {'name': show[1].strip(), 'sites': {'netflix': "http://www.netflix.com/title/" + show[0]}}
				showList.append(show_obj)
		return shows
	def __GetData(self):
		unogsSession = requests.Session()
		getCgiUrlBlob = unogsSession.get('http://unogs.com/search')
		getCgiUrlRegex = 'var cgiurl=\'([^\&"]*)\';'
		
		cgiUrl = re.findall(getCgiUrlRegex, getCgiUrlBlob.text)[0]
		headers = {
			'Referer': 'http://unogs.com/search/?q=-!1900,2016-!0,5-!0,10-!7424-!Any-!Any-!Any&cl=46,&st=adv&ob=Relevance',
			'Accept': 'application/json, text/javascript, */*; q=0.01'
		}
		dataBlob = unogsSession.get('http://unogs.com' + cgiUrl + '&q=-!1900,2016-!0,5-!0,10-!7424-!Any-!Any-!Any&t=ns&cl=46,&st=adv&ob=Relevance', headers = headers)
		return json.loads(dataBlob.text)["ITEMS"]
		
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
sources = [Crunchyroll(), Netflix(), Daisuki(), Viewster()]
for source in sources:
	source.UpdateShowList(shows)
	print('finished a site')
shows = sorted(shows, key = lambda show: show['name'].lower())
out_file = open('../public/data/uk.json', 'w')
json.dump(shows, out_file)
print('done')