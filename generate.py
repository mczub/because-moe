import requests
import json
import re
from abc import ABCMeta, abstractmethod
import string
from unidecode import unidecode

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
		for show in self.__shows['data']:
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
		blob = requests.get('http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&genre=anime&sort=release_with_popularity&_language=en&_region=us&items_per_page=1000&position=0&region=us&locale=en&language=en&access_token=' + oauth_key)
		return json.loads(blob.text)
		
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
		
shows = []
sources = [Crunchyroll(), Funimation(), Hulu(), Netflix()]
for source in sources:
	source.UpdateShowList(shows)
shows = sorted(shows, key = lambda show: show['name'].lower())
out_file = open('./bcmoe.json', 'w')
json.dump(shows, out_file)
print('done')