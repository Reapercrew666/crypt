# -*- coding: utf-8 -*-

import os,re,sys,xbmc,xbmcaddon,json,base64,urllib,urlparse,requests,shutil,xbmcplugin,xbmcgui,socket,urllib2
from xbmcplugin import addDirectoryItem, endOfDirectory
import datetime, time


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

def xumo_channels(url):
    User_Agent = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)"
    headers = {'User-Agent': User_Agent}
    base_api = "https://valencia-app-mds.xumo.com/v2/"
    url = 'http://www.xumo.tv'

    response = requests.get(url).text
    match = json.loads(re.compile('__JOBS_REHYDRATE_STATE__=(.+?);</script>',re.DOTALL).findall(response)[0])
    geoId = match["jobs"]["1"]["data"]["geoId"]
    chanId = match["jobs"]["1"]["data"]["channelListId"]

    Chan = (base_api+('channels/list/%s.json?sort=hybrid&geoId=%s')%(chanId, geoId))
    response = requests.get(Chan, headers=headers).text
    res = json.loads(response)
    item = res['channel']['item']
    items = sorted(list(item), key=lambda item: item['title'])
    link = ""
    for c in items:
        title = c['title'].encode('utf-8')
        check = xumo_bad(title)
        if check == False:
            summary = c['description'].encode('utf-8')
            chid   = c['guid']['value'].encode('utf-8')
            icon = 'https://image.xumo.com/v1/channels/channel/%s/512x512.png?type=color_onBlack'%chid
            url = "%s**%s**%s"% (title, chid, icon)
            addDirVid(title,url,4,icon,addon_fanart,summary)
        else:
            pass

def xumo_link(url):
    name = url.split("**")[0]
    chid = url.split("**")[1]
    iconimage = url.split("**")[2]
    User_Agent = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)"
    headers = {'User-Agent': User_Agent}
    base_api = "https://valencia-app-mds.xumo.com/v2/"
    on_url = base_api+"channels/channel/%s/onnow.json?f=title&f=descriptions#descriptions"%(chid)
    response = requests.get(on_url, headers=headers).text
    res = json.loads(response)
    assets = res['id']
    meta_url = base_api+"assets/asset/%s.json?f=title&f=providers&f=descriptions&f=runtime&f=availableSince"%(assets)
    response = requests.get(meta_url, headers=headers).text
    res = json.loads(response)
    try:
        link = res['providers'][0]['sources'][0]['uri']
    except:
        link = "none"
    is_folder = False       
    liz = xbmcgui.ListItem(name, path=link)
    infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

def xumo_ondemand(url):
    User_Agent = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)"
    headers = {'User-Agent': User_Agent}
    base_api = "https://valencia-app-mds.xumo.com/v2/"
    url = 'http://www.xumo.tv'

    response = requests.get(url).text
    match = json.loads(re.compile('__JOBS_REHYDRATE_STATE__=(.+?);</script>',re.DOTALL).findall(response)[0])
    geoId = match["jobs"]["1"]["data"]["geoId"]
    chanId = match["jobs"]["1"]["data"]["channelListId"]

    Chan = (base_api+('channels/list/%s.json?sort=hybrid&geoId=%s')%(chanId, geoId))
    response = requests.get(Chan, headers=headers).text
    res = json.loads(response)
    item = res['channel']['item']
    items = sorted(list(item), key=lambda item: item['title'])
    for c in items:
        title = c['title'].encode('utf-8')
        num = c['number']
        chid = c['guid']['value']
        icon = 'https://image.xumo.com/v1/channels/channel/%s/512x512.png?type=color_onBlack'%chid
        #fanart = "https://image.xumo.com/v1/channels/channel/%s/248x140.png?type=channelTile"% chid
        summary = c['description'].encode('utf-8')
        url = chid
        addDir(title,chid,5,icon,addon_fanart,summary)

def xumo_ondemand_links(url):
    User_Agent = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)"
    headers = {'User-Agent': User_Agent}
    base_api = "https://valencia-app-mds.xumo.com/v2/"
    chid = url
    lineup_url = base_api+"channels/channel/%s/broadcast.json?hour=22"%chid
    response = requests.get(lineup_url, headers=headers).text
    res = json.loads(response)
    assets = res['assets']
    for a in assets:
        start = a['timestamps']['start']
        end = a['timestamps']['end']
        vodid = a['id']
        meta_url = base_api+"assets/asset/%s.json?f=title&f=providers&f=descriptions&f=runtime&f=availableSince"%(vodid)
        response = requests.get(meta_url, headers=headers).text
        res = json.loads(response)
        show_title = res['title'].encode('utf-8')
        summary = show_title.encode('utf-8')
        try:
            summary = res['descriptions']['large'].encode('utf-8')
        except:
            pass
        try:
            summary = res['descriptions']['medium'].encode('utf-8')
        except:
            pass
        try:
            summary = res['descriptions']['small'].encode('utf-8')
        except:
            pass
        logoid = res['id']
        icon = "https://image.xumo.com/v1/assets/asset/%s/600x340.jpg"% logoid
        try:
            link = res['providers'][0]['sources'][0]['uri']
        except:
            link = "none"   
        addDirVid(show_title,link,101,icon,addon_fanart,summary)

def xumo_bad(name):
    missing = ["ACC Digital Network","Above Average","Adventure Sports Network","Ameba",
    "America's Funniest Home Videos","Architectural Digest","Billboard","Bloomberg Television",
    "CBC NEWS","CHIVE TV","CNET","CollegeHumor","Condé Nast Traveler","Cooking Light",
    "CoolSchool","Copa90","Cycle World","FBE","FOX Sports","Family Feud","Field & Stream",
    "Food52","Football Daily","Fox Deportes","Funny or Die","Futurism","GQ","GameSpot",
    "Glamour","Got Talent Global","Great Big Story","HISTORY","Hard Knocks Fighting Championship",
    "Just For Laughs","Just For Laughs Gags","Kid Genius","MMAjunkie","MOTORVISION.TV",
    "Mashable","Motorcyclist","NEW K.ID","Newsy","Nitro Circus","Nosey","NowThis",
    "Outside TV+","PBS Digital","People Are Awesome","People Magazine","PeopleTV",
    "Popular Science","Real Nosey","Refinery29","Rowan and Martin's Laugh-In",
    "SYFY WIRE","Saveur","Southern Living","Sports Illustrated","TIME Magazine",
    "TMZ","TODAY","The Hollywood Reporter","The Inertia","The New Yorker","The Pet Collective",
    "The Preview Channel","This Is Happening","Titanic Channel","Toon Goggles","USA TODAY News",
    "USA Today SportsWire","Uzoo","Vanity Fair","Vogue","Wochit","World Surf League",
    "Young Hollywood","ZooMoo","batteryPOP","comicbook","eScapes"]
    if name in missing:
        return True
    else:
        return False