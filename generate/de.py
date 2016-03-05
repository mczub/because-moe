import sys
sys.path.append("site-packages")
import json
import string
from unidecode import unidecode
from urllib import parse
from azure.storage.blob import BlobService
from datetime import datetime
import animesources

shows = []

with open('title-map.json') as titlemap_file:
	titlemap = json.load(titlemap_file)
	
with open('multi-season.json') as multiseason_file:
	multiseason = json.load(multiseason_file)
	
with open('azure.json') as azure_file:
	azure_storage = json.load(azure_file)
skip_azure = (azure_storage['account'] == None and azure_storage['key'] == None)

if not skip_azure:
	azure_blob = BlobService(account_name=azure_storage['account'], account_key=azure_storage['key'])

with open('proxies.json') as proxies_file:
	proxy_data = json.load(proxies_file)
	proxy = proxy_data["de"]

sources = [
	animesources.Crunchyroll(titlemap, multiseason, 'de', proxy),
	animesources.NetflixDE(titlemap, multiseason, 'de', proxy),
	animesources.Daisuki(titlemap, multiseason, 'de', proxy),
	animesources.Netzkino(titlemap, multiseason, 'de', proxy),
	animesources.AnimeOnDemand(titlemap, multiseason, 'de', proxy)
]

for source in sources:
	source.UpdateShowList(shows)
	print(source.GetName() + ': ' + str(len(shows)))

with open('alternates.json') as alternates_file:
	alternates = json.load(alternates_file)

for alternate in alternates:
	match_index = next((i for i, x in enumerate(shows) if animesources.compare(x['name'], alternate)), False)
	if (match_index):
		shows[match_index]['alt'] = alternates[alternate]

shows = sorted(shows, key = lambda show: show['name'].lower())
blob = {"lastUpdated": datetime.utcnow().isoformat(), "shows": shows}
out_file = open('de.json', 'w')
json.dump(blob, out_file)
out_file.close()

if not skip_azure:
	azure_blob.put_block_blob_from_path(
		'assets',
		'de.json',
		'de.json',
		x_ms_blob_content_type='application/json'
	)
else:
	print("Skipped Azure upload!")

print('done')