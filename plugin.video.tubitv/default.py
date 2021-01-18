# -*- coding: utf-8 -*-

"""
	TubiTv
	Copyright (C) 2020, TonyH

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

### Imports ###
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs,base64,os,re,requests,json,urllib,urllib2
import __builtin__
from resources.lib import tools

skin_used 			= xbmc.getSkinDir()
addon_id 			= xbmcaddon.Addon().getAddonInfo('id')
ownAddon            = xbmcaddon.Addon(id=addon_id)
tmdb_api_key        = ownAddon.getSetting('tmdb_api_key')
addon_name 			= xbmcaddon.Addon().getAddonInfo('name')
home_folder 		= xbmc.translatePath('special://home/')
addon_folder 		= os.path.join(home_folder, 'addons')
art_path 			= os.path.join(addon_folder, addon_id)
resources_path		= os.path.join(art_path, 'resources')
other_art_path		= os.path.join(resources_path, 'art')
user_data_folder 	= os.path.join(home_folder, 'userdata')
addon_data_folder 	= os.path.join(user_data_folder, 'addon_data')
addon_icon 			= os.path.join(art_path,'icon.png')
addon_fanart 		= os.path.join(art_path,'fanart.jpg')
content_type    	= "movies"


def start():
	url = "https://tubitv.com/oz/containers?isKidsModeEnabled=false&groupStart=1&groupSize=74"
	payload = {}
	headers = {
	  'authority': 'tubitv.com',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
	  'sec-fetch-dest': 'empty',
	  'accept': '*/*',
	  'sec-fetch-site': 'same-origin',
	  'sec-fetch-mode': 'cors',
	  'referer': 'https://tubitv.com/home',
	  'accept-language': 'en-US,en;q=0.9',
	  'cookie': 'deviceId=acb2e6c0-0df9-421d-a57e-8883884121cd; _ga=GA1.2.1067293052.1588638053; _gid=GA1.2.637864145.1588638053; ab.storage.deviceId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%225ce196d7-6c09-1adf-6602-02ad9e11a928%22%2C%22c%22%3A1588638053150%2C%22l%22%3A1588638053150%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IitWazAiLCJ0c2wiOjE1ODg2MzgxMTUsIm52IjowLCJ1cHQiOjE1ODg2MzgwNTIsImx0IjoxNTg4NjM4MTA3fV0.; _gat=1; ab.storage.sessionId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%221e309c17-adca-19ae-120d-d7435f11f4b4%22%2C%22e%22%3A1588639915731%2C%22c%22%3A1588638053146%2C%22l%22%3A1588638115731%7D'
	}
	response = requests.request("GET", url, headers=headers, data = payload).text
	data = json.loads(response)
	cats = data['list']
	for c in cats:
		try:
			try: summary = data['hash'][c]['description'].encode('utf-8')
			except: summary = ""
			name = data['hash'][c]['title'].encode('utf-8')
			sid = data['hash'][c]['id']    
			image = data['hash'][c]['thumbnail']
			fanart = data['hash'][c]['backgrounds'][0]
			if fanart == "": fanart = image
			if name == "Get Fit":
				image = os.path.join(other_art_path, 'getfit.png')
				fanart = os.path.join(other_art_path, 'getfit.png')
			if name == "Spotlight":
				image = os.path.join(other_art_path, 'spotlight.png')
				fanart = os.path.join(other_art_path, 'spotlight.png')
			if name == "Good Eats":
				image = os.path.join(other_art_path, 'goodeats.png')
				fanart = os.path.join(other_art_path, 'goodeats.png')
			if name == "Bollywood Dreams":
				image = os.path.join(other_art_path, 'bollywood.png')
				fanart = os.path.join(other_art_path, 'bollywood.png')
			data2 = sid+"**1"
			tools.addDir(name,data2,2,image,fanart,summary)
		except: pass

def tubitv_cats(url,page):
	url2 = "https://tubitv.com/oz/containers/%s/content?parentId&cursor=10&limit=450&isKidsModeEnabled=false&expand=0"%(url)
	payload = {}
	headers = {
	  'authority': 'tubitv.com',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
	  'sec-fetch-dest': 'empty',
	  'accept': '*/*',
	  'sec-fetch-site': 'same-origin',
	  'sec-fetch-mode': 'cors',
	  'referer': 'https://tubitv.com/home',
	  'accept-language': 'en-US,en;q=0.9',
	  'cookie': 'deviceId=acb2e6c0-0df9-421d-a57e-8883884121cd; _ga=GA1.2.1067293052.1588638053; _gid=GA1.2.637864145.1588638053; ab.storage.deviceId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%225ce196d7-6c09-1adf-6602-02ad9e11a928%22%2C%22c%22%3A1588638053150%2C%22l%22%3A1588638053150%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IitWazAiLCJ0c2wiOjE1ODg2MzgxMTUsIm52IjowLCJ1cHQiOjE1ODg2MzgwNTIsImx0IjoxNTg4NjM4MTA3fV0.; ab.storage.sessionId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%221e309c17-adca-19ae-120d-d7435f11f4b4%22%2C%22e%22%3A1588639954679%2C%22c%22%3A1588638053146%2C%22l%22%3A1588638154679%7D'
	}
	response = requests.request("GET", url2, headers=headers, data = payload).text
	data = json.loads(response)
	children = data['containersHash'][url]['children']
	if page == "1": x = children[0:75]
	elif page == "2": x = children[75:150]
	elif page == "3": x = children[150:225]
	elif page == "4": x = children[225:300]
	elif page == "5": x = children[300:375]
	elif page == "6": x = children[375:450]
	elif page == "7": x = children[450:525]
	page = int(page) +1
	for c in x:
		name = data['contents'][c]['title'].encode('utf-8')
		check = data['contents'][c]['availability_duration']    
		sid = data['contents'][c]['id']
		summary = data['contents'][c]['description'].encode('utf-8')
		image = data['contents'][c]['posterarts'][0]
		try: fanart = data['contents'][c]['backgrounds'][0]            
		except: fanart = addon_fanart
		if check <1:
			tools.addDir(name,c,3,image,fanart,summary)
		else:
			year = data['contents'][c]['year']
			try: duration = data['contents'][c]['duration']
			except: duration = ""
			try: rating  = data['contents'][c]['ratings'][0]['code']
			except: rating = ""
			try: actors = data['contents'][c]['actors']
			except: actors = []
			try: genre = data['contents'][c]['tags'][0]
			except: genre = ""
			tools.addDirMeta(name,sid,4,image,fanart,summary,year,actors,rating,duration,genre)
	data2 = url+"**"+str(page)
	tools.addDir2('Next Page',data2,2,'http://www.clker.com/cliparts/a/f/2/d/1298026466992020846arrow-hi.png',addon_fanart,'')

def tubitv_shows(url):
	url = "https://tubitv.com/oz/videos/%s/content"%(url)
	payload = {}
	headers = {
	  'authority': 'tubitv.com',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
	  'sec-fetch-dest': 'empty',
	  'accept': '*/*',
	  'sec-fetch-site': 'same-origin',
	  'sec-fetch-mode': 'cors',
	  'referer': 'https://tubitv.com/movies/522070/open_season_2',
	  'accept-language': 'en-US,en;q=0.9',
	  'cookie': 'deviceId=acb2e6c0-0df9-421d-a57e-8883884121cd; _ga=GA1.2.1067293052.1588638053; _gid=GA1.2.637864145.1588638053; ab.storage.deviceId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%225ce196d7-6c09-1adf-6602-02ad9e11a928%22%2C%22c%22%3A1588638053150%2C%22l%22%3A1588638053150%7D; ab.storage.sessionId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%221813a4c9-485e-9f8c-fc66-4d5861175baa%22%2C%22e%22%3A1588651125555%2C%22c%22%3A1588649325553%2C%22l%22%3A1588649325555%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IjBmSm0iLCJ0c2wiOjE1ODg2NTI3MTMsIm52IjoxLCJ1cHQiOjE1ODg2MzgxNTQsImx0IjoxNTg4NjUyNzExfV0.; _gat=1',
	  'if-none-match': 'W/"9fc-s+qOH8lZhrKqiowHa18So4WAGOE"'
	}
	response = requests.request("GET", url, headers=headers, data = payload).text
	data = json.loads(response)
	children = data['children']
	for child in children:
		Children = child['children']
		for c in Children:
			sid = c['id']
			name = c['title'].encode('utf-8')
			try: summary = c['description'].encode('utf-8')
			except: summary = ""
			try: image = c['thumbnails'][0]
			except: image = addon_icon
			try: fanart = c['backgrounds'][0] 
			except: fanart = addon_fanart
			year = c['year']
			duration = c['duration']
			try: rating  = c['ratings'][0]['code']
			except: rating = ""
			try: actors = c['actors']
			except: actors = []
			try: genre = c['tags'][0]
			except: genre = ""
			tools.addDirMeta(name,sid,4,image,fanart,summary,year,actors,rating,duration,genre)

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

params=get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None


try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage=urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
try:
	description=urllib.unquote_plus(params["description"])
except:
	pass
try:
	query=urllib.unquote_plus(params["query"])
except:
	pass
try:
	type=urllib.unquote_plus(params["type"])
except:
	pass

	### Modes ###
if mode==None or url==None or len(url)<1:
	start()
elif mode==2:
	sid = url.split("**")[0]
	page = url.split("**")[-1]
	tubitv_cats(sid,page)
elif mode==3:
	tubitv_shows(url)
elif mode==4:
	url2 = "https://tubitv.com/oz/videos/%s/content"%(url)
	payload = {}
	headers = {
	  'authority': 'tubitv.com',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
	  'sec-fetch-dest': 'empty',
	  'accept': '*/*',
	  'sec-fetch-site': 'same-origin',
	  'sec-fetch-mode': 'cors',
	  'referer': 'https://tubitv.com/movies/522070/open_season_2',
	  'accept-language': 'en-US,en;q=0.9',
	  'cookie': 'deviceId=acb2e6c0-0df9-421d-a57e-8883884121cd; _ga=GA1.2.1067293052.1588638053; _gid=GA1.2.637864145.1588638053; ab.storage.deviceId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%225ce196d7-6c09-1adf-6602-02ad9e11a928%22%2C%22c%22%3A1588638053150%2C%22l%22%3A1588638053150%7D; ab.storage.sessionId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%221813a4c9-485e-9f8c-fc66-4d5861175baa%22%2C%22e%22%3A1588651125555%2C%22c%22%3A1588649325553%2C%22l%22%3A1588649325555%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IjBmSm0iLCJ0c2wiOjE1ODg2NTI3MTMsIm52IjoxLCJ1cHQiOjE1ODg2MzgxNTQsImx0IjoxNTg4NjUyNzExfV0.; _gat=1',
	  'if-none-match': 'W/"9fc-s+qOH8lZhrKqiowHa18So4WAGOE"'
	}
	response = requests.request("GET", url2, headers=headers, data = payload).text
	data = json.loads(response)
	res = json.dumps(data, indent=2)
	UA = "|User-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
	link = data['video_resources'][0]['manifest']['url']+UA	
	liz = xbmcgui.ListItem(name, path=link)
	infoLabels={"title": name}
	liz.setInfo(type="video", infoLabels=infoLabels)
	liz.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
elif mode==5:
	tools.Get_Trailer(url,name)
elif mode==6:
	tools.Get_Series_Trailer(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))