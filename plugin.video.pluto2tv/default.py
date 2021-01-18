# -*- coding: utf-8 -*-

"""
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
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs,os,re,requests,json,urllib,urllib2
from resources.lib import tools,uepgplutotv

skin_used 			= xbmc.getSkinDir()
addon_id 			= xbmcaddon.Addon().getAddonInfo('id')
addon_name 			= xbmcaddon.Addon().getAddonInfo('name')
home_folder 		= xbmc.translatePath('special://home/')
addon_folder 		= os.path.join(home_folder, 'addons')
art_path 			= os.path.join(addon_folder, addon_id)
resources_path		= os.path.join(art_path, 'resources')
user_data_folder 	= os.path.join(home_folder, 'userdata')
addon_data_folder 	= os.path.join(user_data_folder, 'addon_data')
ownAddon            = xbmcaddon.Addon(id=addon_id)
icon 				= os.path.join(art_path,'icon.png')
fanart 				= os.path.join(art_path,'fanart.jpg')
content_type    	= "movies"

ADDON_ID      		= 'plugin.video.pluto2tv'
REAL_SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    		= REAL_SETTINGS.getAddonInfo('path')
PlutoSkinPath     	= os.path.join(ADDON_PATH,'plutoepgskin')

def start():
	tools.addDir("[COLOR=orange]Pluto Tv Guide[/COLOR]","pluto_guide",1,icon,fanart,"Pluto Tv Guide")
	tools.addDir("[COLOR=orange]Pluto Tv Channels[/COLOR]","pluto_channels",2,icon,fanart,"Pluto Tv Channels")
	tools.addDir("[COLOR=orange]Pluto Tv Movie Channels[/COLOR]","pluto_movies",3,icon,fanart,"Pluto Tv Movie Channels")
	tools.addDir("[COLOR=orange]Pluto Tv 24-7[/COLOR]","pluto_24-7",4,icon,fanart,"Pluto Tv 24-7")
	tools.addDir("[COLOR=orange]Pluto Tv On Demand[/COLOR]","pluto_ondemand",5,icon,fanart,"Pluto Tv On Demand")	

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
elif mode==1:
	Guide_Data = uepgplutotv.buildguide()
	xbmc.executebuiltin("RunScript(script.module.uepg,json=%s&skin_path=%s&refresh_path=%s&refresh_interval=%s&row_count=%s)"%(urllib.quote(json.dumps(Guide_Data)),urllib.quote(PlutoSkinPath),(urllib.quote(sys.argv[0]+"?mode=21")),("7200"),"7"))
elif mode==2:
	tools.pluto(url)
elif mode==3:
	tools.plutomovies(url)
elif mode==4:
	tools.pluto247(url)
elif mode==5:
	tools.plutoondemand(url)
elif mode==6:
	tools.plutoondemand_movies(url)
elif mode==7:
	tools.plutoondemand_series(url)
elif mode==8:
	tools.plutoondemand_episodes(url)
elif mode==101 or mode==102:
	liz = xbmcgui.ListItem(name, path=url)
	infoLabels={"title": name}
	liz.setInfo(type="video", infoLabels=infoLabels)
	liz.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

xbmcplugin.endOfDirectory(int(sys.argv[1]))