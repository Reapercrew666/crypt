# -*- coding: utf-8 -*-

import os,re,sys,xbmc,xbmcaddon,json,base64,requests,xbmcplugin,xbmcgui,urllib
from xbmcplugin import addDirectoryItem, endOfDirectory

addon_id            = xbmcaddon.Addon().getAddonInfo('id')
ownAddon            = xbmcaddon.Addon(id=addon_id)
tmdb_api_key        = ownAddon.getSetting('tmdb_api_key')
addon_name          = xbmcaddon.Addon().getAddonInfo('name')
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder, 'addons')
art_path            = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(art_path, 'resources')
other_art_path      = os.path.join(resources_path, 'art')
lib_path            = os.path.join(resources_path, 'lib')
skin_used           = xbmc.getSkinDir()
addon_icon          = os.path.join(art_path,'icon.png')
addon_fanart        = os.path.join(art_path,'fanart.jpg')
content_type        = "movies"

def Build_url(mode, url, name):
    return sys.argv[0]+"?mode=%s" % mode+"&url=%s" % urllib.quote_plus(url)+"&name=%s"% urllib.quote_plus(name) 

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('fanart_image', fanart)
    cm = []
    if mode==3:
        cm.append(('Information', 'XBMC.Action(Info)'))
        cm.append(('Trailer', 'XBMC.RunPlugin({})'.format(Build_url(6,url,name))))
        liz.addContextMenuItems(cm,replaceItems=True)
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
    else:
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

def addDir2(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('fanart_image', fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    if skin_used == 'skin.xonfluence':
        xbmc.executebuiltin('Container.SetViewMode(503)') # "MediaListView2" view
    elif skin_used == 'skin.confluence':
        xbmc.executebuiltin('Container.SetViewMode(503)') # "MediaListView2" view
    elif skin_used == 'skin.aeon.nox':
        xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
    elif skin_used == 'skin.aeon.embuary':
        xbmc.executebuiltin('Container.SetViewMode(59)') # "Big-List" view.
    else:
        xbmc.executebuiltin('Container.SetViewMode(50)') # "Default-View for all" view.
    return ok
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addDirMeta(name,url,mode,iconimage,fanart,description,year,cast,rating,runtime,genre):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)+"&fanart="+urllib.quote_plus(fanart)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,"Rating":rating,"Year":year,"Duration":runtime,"Cast":cast,"Genre":genre})
    liz.setProperty('fanart_image', fanart)
    cm = []
    if mode==4:
        liz.setProperty('IsPlayable', 'true')
        cm.append(('Information', 'XBMC.Action(Info)'))
        cm.append(('Trailer', 'XBMC.RunPlugin({})'.format(Build_url(5,url,name))))
        liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
        liz.setProperty('fanart_image', fanart)
        liz.addContextMenuItems(cm,replaceItems=True)
        if skin_used == 'skin.xonfluence':
            xbmc.executebuiltin('Container.SetViewMode(503)') # "MediaListView2" view
        elif skin_used == 'skin.confluence':
            xbmc.executebuiltin('Container.SetViewMode(503)') # "MediaListView2" view
        elif skin_used == 'skin.aeon.nox':
            xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
        elif skin_used == 'skin.aeon.embuary':
            xbmc.executebuiltin('Container.SetViewMode(59)') # "Big-List" view.
        else:
            xbmc.executebuiltin('Container.SetViewMode(50)') # "Default-View for all" view.
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    else:
        liz.addContextMenuItems(cm,replaceItems=True)
        if skin_used == 'skin.xonfluence':
            xbmc.executebuiltin('Container.SetViewMode(503)') # "MediaListView2" view
        elif skin_used == 'skin.confluence':
            xbmc.executebuiltin('Container.SetViewMode(503)') # "MediaListView2" view
        elif skin_used == 'skin.aeon.nox':
            xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
        elif skin_used == 'skin.aeon.embuary':
            xbmc.executebuiltin('Container.SetViewMode(59)') # "Big-List" view.
        else:
            xbmc.executebuiltin('Container.SetViewMode(50)') # "Default-View for all" view.
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok
    xbmcplugin.endOfDirectory

def Get_Trailer(url,name):
    turl = "https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1&include_adult=false"%(tmdb_api_key,name.replace(" ","%20"))
    html = requests.get(turl).json()
    try:
        Id = html['results'][0]['id']
        turl2 = "https://api.themoviedb.org/3/movie/%s/videos?api_key=%s&language=en-US"%(Id, tmdb_api_key)
        html2 = requests.get(turl2).json()
        trail_key = html2['results'][0]['key']
        liz = xbmcgui.ListItem(name)
        infoLabels={"title": name}
        liz.setInfo(type="video", infoLabels=infoLabels)
        liz.setProperty('IsPlayable', 'true')
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/play/?video_id="+trail_key+")")
    except: xbmc.executebuiltin('Notification(Not Found,No Trailer Found,5000)')

def Get_Series_Trailer(url,name):
    turl = "https://api.themoviedb.org/3/search/tv?api_key=%s&language=en-US&page=1&query=%s&include_adult=false"%(tmdb_api_key,name.replace(" ","%20"))
    html = requests.get(turl).json()
    try:
        Id = html['results'][0]['id']
        turl2 = "https://api.themoviedb.org/3/tv/%s/videos?api_key=%s&language=en-US"%(Id, tmdb_api_key)
        html2 = requests.get(turl2).json()
        trail_key = html2['results'][0]['key']
        liz = xbmcgui.ListItem(name)
        infoLabels={"title": name}
        liz.setInfo(type="video", infoLabels=infoLabels)
        liz.setProperty('IsPlayable', 'true')
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/play/?video_id="+trail_key+")")
    except: xbmc.executebuiltin('Notification(Not Found,No Trailer Found,5000')