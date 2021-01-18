# -*- coding: utf-8 -*-

"""
    Copyright (C) 2020, TonyH
    Module for the pluto2tv addon
    
"""

import os,re,sys,xbmc,xbmcaddon,json,base64,urllib,urlparse,requests,shutil,xbmcplugin,xbmcgui,socket,urllib2
from xbmcplugin import addDirectoryItem, endOfDirectory
import datetime, time
from airtable.airtable import Airtable


addon_id            = xbmcaddon.Addon().getAddonInfo('id')
addon_name          = xbmcaddon.Addon().getAddonInfo('name')
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder, 'addons')
art_path            = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(art_path, 'resources')
lib_path            = os.path.join(resources_path, 'lib')
ownAddon            = xbmcaddon.Addon(id=addon_id)
skin_used           = xbmc.getSkinDir()
addon_icon          = os.path.join(art_path,'icon.png')
addon_fanart        = os.path.join(art_path,'fanart.jpg')
content_type        = "movies"

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('fanart_image', fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    if skin_used == 'skin.xonfluence':
        xbmc.executebuiltin('Container.SetViewMode(515)') # "MediaListView2" view
    elif skin_used == 'skin.confluence':
        xbmc.executebuiltin('Container.SetViewMode(515)') # "MediaListView2" view
    elif skin_used == 'skin.aeon.nox':
        xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
    elif skin_used == 'skin.aeon.embuary':
        xbmc.executebuiltin('Container.SetViewMode(59)') # "Big-List" view.
    else:
        xbmc.executebuiltin('Container.SetViewMode(50)') # "Default-View for all" view.
    return ok
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addDirVid(name,url,mode,iconimage,fanart,description):
    ok=True
    liz = xbmcgui.ListItem(label=name, thumbnailImage=iconimage)
    liz.setProperty('fanart_image', fanart)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('IsPlayable', 'true')
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    if mode== 102:
        liz.addContextMenuItems([('EPG Data', 'RunScript(special://home/addons/plugin.video.pluto2tv/resources/lib/plutoepg.py, %s)'%u,)])
    is_folder = False
    if skin_used == 'skin.xonfluence':
        xbmc.executebuiltin('Container.SetViewMode(515)') # "MediaListView2" view
    elif skin_used == 'skin.confluence':
        xbmc.executebuiltin('Container.SetViewMode(515)') # "MediaListView2" view
    elif skin_used == 'skin.aeon.nox':
        xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
    elif skin_used == 'skin.aeon.embuary':
        xbmc.executebuiltin('Container.SetViewMode(59)') # "Big-List" view.
    else:
        xbmc.executebuiltin('Container.SetViewMode(50)') # "Default-View for all" view.
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)        
    return ok
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def pluto(url):
    at = Airtable('app2G6Yr2AEypizyg','plutotv',api_key='keyOHaxsTGzHU9EEh')
    data = at.get_all(maxRecords=1200, sort='name')
    for field in data:
        res = field['fields']
        iconimage = res['thumbnail']
        fanart = res['fanart']
        link1 = res['link1']        
        name = res['name'].encode('utf-8')
        summary = res['summary'].encode('utf-8')
        try:
            addDirVid(name,link1,102,iconimage,fanart,summary)
        except:
            pass 

def plutomovies(url):
    at = Airtable('appW0bIvkEfWkLLu8','plutomovies',api_key='keyOHaxsTGzHU9EEh')
    data = at.get_all(maxRecords=1200, sort='name')
    for field in data:
        res = field['fields']
        iconimage = res['thumbnail']
        fanart = res['fanart']
        link1 = res['link1']        
        name = res['name'].encode('utf-8')
        summary = res['summary'].encode('utf-8')
        try:
            addDirVid(name,link1,102,iconimage,fanart,summary)
        except:
            pass

def pluto247(url):
    at = Airtable('appmHTSTnsC4gXryQ','plutobinge',api_key='keyOHaxsTGzHU9EEh')
    data = at.get_all(maxRecords=1200, sort='name')
    for field in data:
        res = field['fields']
        iconimage = res['thumbnail']
        fanart = res['fanart']
        link1 = res['link1']        
        name = res['name'].encode('utf-8')
        try:
            addDirVid(name,link1,101,iconimage,addon_fanart,name)
        except:
            pass
 

def plutoondemand(url):
    url = "https://api.pluto.tv/v3/vod/categories?includeItems=true&deviceType=web&"
    data = requests.get(url).json()
    cats = data['categories']
    for c in cats:
        name = c['name'].encode('utf-8')
        addDir(name,name,6,addon_icon,addon_fanart,name)


def plutoondemand_movies(url):
    endurl = "?terminate=false&deviceId=5451cc22-6479-4d0b-8b60-af53120675a8&deviceVersion=80.0.3987.116&appVersion=5.0.3-5a69f0421bfaa21acf57c7f54f9914128359c64e&deviceType=web&deviceMake=Chrome&sid=4f03fc35-7f02-4501-b8e1-030fe0777c37&advertisingId=&deviceLat=34.620900&deviceLon=-120.192200&deviceDNT=0&deviceModel=Chrome&userId=&embedPartner=&appName=web&serverSideAds=true&architecture=&paln=&includeExtendedEvents=false|User-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    catname = url
    url = "https://api.pluto.tv/v3/vod/categories?includeItems=true&deviceType=web&"
    data = requests.get(url).json()
    cats = data['categories']
    for c in cats:
        name = c['name'].encode('utf-8')
        if catname == name:
            items = c['items']
            for m in items:
                Type = m['type']
                chid = m['_id']
                if Type == "movie":
                    movie = m['name'].encode('utf-8')
                    summary = m['summary'].encode('utf-8')
                    fanart = m['featuredImage']['path']
                    iconimage = m['covers'][0]['url']
                    link = m['stitched']['urls'][0]['url'].split("?")[0]+endurl
                    addDirVid(movie,link,101,iconimage,fanart,summary) 
                elif Type == "series":
                    seanum = m['seasonsNumbers']
                    show = m['name'].encode('utf-8')
                    summary = m['summary'].encode('utf-8')
                    fanart = m['featuredImage']['path']
                    images = m['covers']
                    iconimage = [image.get('url',[]) for image in images if image.get('aspectRatio','') == '1:1'][0]
                    link = chid+"**"+iconimage
                    addDir(show,link,7,iconimage,fanart,summary)         

def plutoondemand_series(url):
    chid = url.split("**")[0]
    iconimage = url.split("**")[-1]
    url2 = "https://api.pluto.tv/v3/vod/series/%s/seasons?includeItems=true&deviceType=web&"%chid
    data = requests.get(url2).json()
    summary = data['summary'].encode('utf-8')
    fanart = data['featuredImage']['path']
    seasons = data['seasons']
    for s in seasons:
        number = "Season "+str(s['number'])
        link = number+"**"+fanart+"**"+chid
        addDir(number,link,8,iconimage,fanart,summary)
              

def plutoondemand_episodes(url):
    endurl = "?terminate=false&deviceId=5451cc22-6479-4d0b-8b60-af53120675a8&deviceVersion=80.0.3987.116&appVersion=5.0.3-5a69f0421bfaa21acf57c7f54f9914128359c64e&deviceType=web&deviceMake=Chrome&sid=4f03fc35-7f02-4501-b8e1-030fe0777c37&advertisingId=&deviceLat=34.620900&deviceLon=-120.192200&deviceDNT=0&deviceModel=Chrome&userId=&embedPartner=&appName=web&serverSideAds=true&architecture=&paln=&includeExtendedEvents=false|User-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    snumber = url.split("**")[0]
    snumber = snumber.split("Season ")[-1]
    fanart = url.split("**")[1]
    chid = url.split("**")[-1]
    url2 = "https://api.pluto.tv/v3/vod/series/%s/seasons?includeItems=true&deviceType=web&"%chid
    data = requests.get(url2).json()
    seasons = data['seasons']
    for s in seasons:
        number = s['number']
        if str(number) == snumber:
            episodes = s['episodes']
            for e in episodes:
                images = e['covers']
                iconimage = [image.get('url',[]) for image in images if image.get('aspectRatio','') == '4:3'][0]
                epname = e['name'].encode('utf-8')
                summary = e['description'].encode('utf-8')
                link = e['stitched']['urls'][0]['url'].split("?")[0]+endurl
                addDirVid(epname,link,101,iconimage,fanart,summary)
