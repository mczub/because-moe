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
		blob = requests.get('http://www.crunchyroll.com/videos/anime/alpha?group=all')
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
		blob = requests.get('http://www.funimation.com/videos/episodes')
		regex = '<a class=\"fs16 bold\" href=\"([^\"]*)\">([^\"]*)</a>'
		return re.findall(regex, blob.text)
		
class Hulu(AnimeSource):
	def __init(self):
		self.__shows = []
	def UpdateShowList(self, showList):
		self.__shows = self.__GetData()
		transtable = {ord(c): None for c in string.punctuation}
		for show in self.__shows:
			#print(show['show']['name'])
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show['show']['name'])), False)
			if (match_index):
				shows[match_index]['sites']['hulu'] = 'http://www.hulu.com/' + show['show']['canonical_name']
			else:
				show_obj = {'name': show['show']['name'], 'sites': {'hulu': 'http://www.hulu.com/' + show['show']['canonical_name']}}
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
		blob = requests.get('http://animeonnetflix.com/anime-shows-on-netflix/')
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
			match_index = next((i for i, x in enumerate(showList) if compare(x['name'], show['title'])), False)
			if (match_index):
				shows[match_index]['sites']['daisuki'] = True
			else:
				show_obj = {'name': show['title'], 'sites': {'daisuki': True}}
				showList.append(show_obj)

		return shows
	
	def __GetData(self):
		blob = requests.get('http://www.daisuki.net/fastAPI/anime/search/?')
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
		api_blob = requests.get('https://www.viewster.com/')
		api_token = api_blob.cookies['api_token']
		headers = {'Auth-token': parse.unquote(api_token)}
		anime_blob = requests.get('https://public-api.viewster.com/series?pageSize=100&pageIndex=1&genreId=58', headers = headers)
		return json.loads(anime_blob.text)['Items']
		
shows = []
sources = [Crunchyroll(), Funimation(), Hulu(), Netflix(), Daisuki(), Viewster()]
for source in sources:
	source.UpdateShowList(shows)
shows = sorted(shows, key = lambda show: show['name'].lower())
out_file = open('../public/bcmoe.json', 'w')
json.dump(shows, out_file)
print('done')