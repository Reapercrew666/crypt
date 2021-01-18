# -*- coding: utf-8 -*-

import os,re,sys,xbmc,xbmcaddon,json,base64,urllib,urlparse,requests,xbmcplugin,xbmcgui,urllib2
from xbmcplugin import addDirectoryItem, endOfDirectory


addon_id            = xbmcaddon.Addon().getAddonInfo('id')
addon_name          = xbmcaddon.Addon().getAddonInfo('name')
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder, 'addons')
art_path            = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(art_path, 'resources')
lib_path            = os.path.join(resources_path, 'lib')
other_art_path      = os.path.join(resources_path, 'art')
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

def live(url):
    url = "https://tv.jsrdn.com/tv_v5/getfeed.php"
    payload = {}
    headers = {
      'authority': 'tv.jsrdn.com',
      'accept': 'application/json, text/javascript, */*; q=0.01',
      'sec-fetch-dest': 'empty',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
      'origin': 'https://www.distro.tv',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'cors',
      'referer': 'https://www.distro.tv/live',
      'accept-language': 'en-US,en;q=0.9'
    }
    response = requests.request("GET", url, headers=headers, data = payload).content
    data = json.loads(response)
    topics = data['topics']
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == "live":  
	        addDir(title,title,3,addon_icon,addon_fanart,title) 

def vod(url):
    url = "https://tv.jsrdn.com/tv_v5/getfeed.php"
    payload = {}
    headers = {
      'authority': 'tv.jsrdn.com',
      'accept': 'application/json, text/javascript, */*; q=0.01',
      'sec-fetch-dest': 'empty',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
      'origin': 'https://www.distro.tv',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'cors',
      'referer': 'https://www.distro.tv/live',
      'accept-language': 'en-US,en;q=0.9'
    }
    response = requests.request("GET", url, headers=headers, data = payload).content
    data = json.loads(response)
    topics = data['topics']
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == "vod":  
	        addDir(title,title,4,addon_icon,addon_fanart,title) 

def live_cats(url):
    url2 = "https://tv.jsrdn.com/tv_v5/getfeed.php"
    payload = {}
    headers = {
      'authority': 'tv.jsrdn.com',
      'accept': 'application/json, text/javascript, */*; q=0.01',
      'sec-fetch-dest': 'empty',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
      'origin': 'https://www.distro.tv',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'cors',
      'referer': 'https://www.distro.tv/live',
      'accept-language': 'en-US,en;q=0.9'
    }
    response = requests.request("GET", url2, headers=headers, data = payload).content
    data = json.loads(response)     
    topics = data['topics']
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == "live":
            if url == title:
                shows = t['shows']
                for s in shows:
                    s= str(s)
                    Show = data['shows'][s]['title'].encode('utf-8')
                    rating = data['shows'][s]['rating']
                    summary = data['shows'][s]['description'].encode('utf-8')
                    image = data['shows'][s]['img_thumbv']
                    fanart = data['shows'][s]['img_poster']
                    year = data['shows'][s]['pubdate']
                    res = s+"**"+fanart
                    link = data['shows'][s]['seasons'][0]['episodes'][0]['content']['url']
                    addDirVid(Show,link,101,image,fanart,summary)

def vod_cats(url):
    url2 = "https://tv.jsrdn.com/tv_v5/getfeed.php"
    payload = {}
    headers = {
      'authority': 'tv.jsrdn.com',
      'accept': 'application/json, text/javascript, */*; q=0.01',
      'sec-fetch-dest': 'empty',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
      'origin': 'https://www.distro.tv',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'cors',
      'referer': 'https://www.distro.tv/live',
      'accept-language': 'en-US,en;q=0.9'
    }
    response = requests.request("GET", url2, headers=headers, data = payload).content
    data = json.loads(response)     
    topics = data['topics']
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == "vod":
            if url == title:
                shows = t['shows']
                for s in shows:
                    s= str(s)
                    Show = data['shows'][s]['title'].encode('utf-8')
                    rating = data['shows'][s]['rating']
                    summary = data['shows'][s]['description'].encode('utf-8')
                    image = data['shows'][s]['img_thumbv']
                    fanart = data['shows'][s]['img_poster']
                    year = data['shows'][s]['pubdate']
                    episodes = data['shows'][s]['seasons'][0]['episodes']
                    res = s+"**"+fanart
                    if len(episodes)>1:
                        addDir(Show,res,5,image,fanart,summary)
                    else:
                        link = data['shows'][s]['seasons'][0]['episodes'][0]['content']['url']
                        addDirVid(Show,link,101,image,fanart,summary)	

def distro_seasons(url):
    sid = url.split("**")[0]
    fanart = url.split("**")[-1]
    url2 = "https://tv.jsrdn.com/tv_v5/getfeed.php"
    payload = {}
    headers = {
      'authority': 'tv.jsrdn.com',
      'accept': 'application/json, text/javascript, */*; q=0.01',
      'sec-fetch-dest': 'empty',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
      'origin': 'https://www.distro.tv',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'cors',
      'referer': 'https://www.distro.tv/live',
      'accept-language': 'en-US,en;q=0.9'
    }
    response = requests.request("GET", url2, headers=headers, data = payload).content
    data = json.loads(response) 
    episodes = data['shows'][sid]['seasons'][0]['episodes']
    for e in episodes:
        title = e['title'].encode('utf-8')
        image = e['img_thumbh']
        summary = e['description'].encode('utf-8')
        link = e['content']['url']
        addDirVid(title,link,101,image,fanart,summary)