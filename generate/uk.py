import sys
sys.path.append("site-packages")
import json
import string
from unidecode import unidecode
from urllib import parse
from azure.storage.blob import BlockBlobService
from datetime import datetime
import animesources

indexedShows = {}
shows = []

with open('title-map.json') as titlemap_file:
	titlemap = json.load(titlemap_file)
with open('multi-season.json') as multiseason_file:
	multiseason = json.load(multiseason_file)
with open('azure.json') as azure_file:
	azure_storage = json.load(azure_file)
azure_blob = BlockBlobService(account_name=azure_storage['account'], account_key=azure_storage['key'])
with open('proxies.json') as proxies_file:
	proxy_data = json.load(proxies_file)
	proxy = proxy_data['uk']
sources = [
	animesources.Crunchyroll(titlemap, multiseason, 'uk', proxy), 
	animesources.Funimation(titlemap, multiseason, 'gb', proxy),
	animesources.Netflix(titlemap, multiseason, 'uk', proxy), 
	animesources.Viewster(titlemap, multiseason, 'uk', proxy),
	animesources.Animax(titlemap, multiseason, 'uk', proxy),
	animesources.HiDive(titlemap, multiseason, 'uk', proxy),
	animesources.AmazonPrime(titlemap, multiseason, 'uk', proxy)]
for source in sources:
	source.UpdateShowList(indexedShows)
	print(source.GetName() + ': ' + str(len(indexedShows)))
shows = indexedShows.values()
with open('alternates.json') as alternates_file:
	alternates = json.load(alternates_file)
for alternate in alternates:
	match_index = next((i for i, x in enumerate(shows) if animesources.compare(x['name'], alternate)), False)
	if (match_index):
		shows[match_index]['alt'] = alternates[alternate]
shows = sorted(shows, key = lambda show: show['name'].lower())
blob = {"lastUpdated": datetime.utcnow().isoformat(), "shows": shows}
out_file = open('uk.json', 'w')
json.dump(blob, out_file)
out_file.close()
azure_blob.create_blob_from_path(
	'assets',
	'uk.json',
	'uk.json'
)
print('done')