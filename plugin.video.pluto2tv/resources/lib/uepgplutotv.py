import xbmc,xbmcaddon,xbmcgui,xbmcplugin,base64,os,re,unicodedata,requests,time,string,sys,urllib,urllib2,json,urlparse,datetime,zipfile,shutil,uuid
import __builtin__
from datetime import timedelta
from resources.lib import tools

skin_used           = xbmc.getSkinDir()
addon_id            = xbmcaddon.Addon().getAddonInfo('id')
addon_name          = xbmcaddon.Addon().getAddonInfo('name')
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder, 'addons')
art_path            = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(art_path, 'resources')
user_data_folder    = os.path.join(home_folder, 'userdata')
addon_data_folder   = os.path.join(user_data_folder, 'addon_data')
icon                = os.path.join(art_path,'icon.png')
fanart              = os.path.join(art_path,'fanart.jpg')
content_type        = "movies"


endurl = "?terminate=false&deviceId=5451cc22-6479-4d0b-8b60-af53120675a8&deviceVersion=80.0.3987.116&appVersion=5.0.3-5a69f0421bfaa21acf57c7f54f9914128359c64e&deviceType=web&deviceMake=Chrome&sid=4f03fc35-7f02-4501-b8e1-030fe0777c37&advertisingId=&deviceLat=34.620900&deviceLon=-120.192200&deviceDNT=0&deviceModel=Chrome&userId=&embedPartner=&appName=web&serverSideAds=true&architecture=&paln=&includeExtendedEvents=false|User-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"


def build_link(url):
    agent = "|User-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    if url.endswith('?deviceType='): url = url.replace('deviceType=','deviceType=&deviceMake=&deviceModel=&&deviceVersion=unknown&appVersion=unknown&deviceDNT=0&userId=&advertisingId=&app_name=&appName=&buildVersion=&appStoreUrl=&architecture=&includeExtendedEvents=false')#todo lazy fix replace
    if 'sid' not in url: url = url.replace('deviceModel=&','deviceModel=&' + LANGUAGE(30022)%(getUUID()))
    url = url.replace('deviceType=&','deviceType=web&').replace('deviceMake=&','deviceMake=Chrome&') .replace('deviceModel=&','deviceModel=Chrome&').replace('appName=&','appName=web&')#todo replace with regex!
    url = url+agent
    return url 

sid1 = str(uuid.uuid1())
deviceId1 = str(uuid.uuid4())
BASE_API     = 'https://api.pluto.tv'
BASE_GUIDE = 'https://service-channels.clusters.pluto.tv/v1/guide?start=%s&stop=%s&%s' 

now = datetime.datetime.utcnow()
stime = datetime.datetime(1970,1,1)
nowepoch =  int((now - stime).total_seconds())

def setUUID():
    if REAL_SETTINGS.getSetting("sid1"): return
    REAL_SETTINGS.setSetting("sid1",str(uuid.uuid1()))
    REAL_SETTINGS.setSetting("deviceId1",str(uuid.uuid4()))

def getUUID():
    #return REAL_SETTINGS.getSetting("sid1"), REAL_SETTINGS.getSetting("deviceId1")
    return sid1,deviceId1

def timezone():
    if time.localtime(time.time()).tm_isdst and time.daylight: return time.altzone / -(60*60) * 100
    else: return time.timezone / -(60*60) * 100

def results():
    tz    = str(timezone())
    start = datetime.datetime.now().strftime('%Y-%m-%dT%H:00:00').replace('T','%20').replace(':00:00','%3A00%3A00.000'+tz)
    stop  = (datetime.datetime.now() + datetime.timedelta(hours=6)).strftime('%Y-%m-%dT%H:00:00').replace('T','%20').replace(':00:00','%3A00%3A00.000'+tz)
    return (BASE_GUIDE %(start,stop,'deviceId=%s&deviceMake=Chrome&deviceType=web&deviceVersion=80.0.3987.149&DNT=0&sid=%s&appName=web&appVersion=5.2.2-d60060c7283e0978cc63ba036956b5c1657f8eba'%(deviceId1,sid1)))


def buildguide():
    guidedata = []
    Guide_Data = []
    url = results()
    json_data = requests.get(url).json()
    channels = json_data['channels']
    images = channels[0]['images']
    Images ={}
    for c in channels:
        chData = {}
        shData = []
        images = c['images']
        for i in images:
            imageurl = i['url']
            imagetype = i['type']
            Images.update( {imagetype : imageurl} )
        chlogo = Images['logo']
        chthumb = Images['colorLogoPNG']
        chfanart = Images['featuredImage']
        chhero = Images['hero']
        chname = c['name'].encode('utf-8')
        chsummary = c['summary']
        try:
            link = c['stitched']['urls'][0]['url']
        except:
            link = ""
        try:
            link = c['timelines'][0]['episode']['sourcesWithClipDetails'][0]['url']
            link = link + "?serverSideAds=true|User-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
        except:
            pass
        chnum = c['number']
        chData.update({'channelname': '%s'%chname,
                    'channelnumber': '%s'%chnum,
                    'channellogo': '%s'%chlogo,})
        try:
            timelines = c['timelines']
            for t in timelines:
                sstart = t['start'][0:19]
                starttime = datetime.datetime(*(time.strptime(sstart, "%Y-%m-%dT%H:%M:%S")[0:6]))
                gamestartepoch = int((starttime - stime).total_seconds())
                sstop = t['stop'][0:19]
                stoptime = datetime.datetime(*(time.strptime(sstop, "%Y-%m-%dT%H:%M:%S")[0:6]))
                gamestopepoch = int((stoptime - stime).total_seconds())
                duration = int(gamestopepoch - gamestartepoch)
                sname = t['title'][0:71].encode('utf-8')
                plot = t['episode']['description']
                genre = t['episode']['genre']
                shthumb = t['episode']['series']['featuredImage']['path']
                shData.append({
                               'url': '%s'%link,
                               'plot': '%s'%plot,
                               'fanart': '%s'%chfanart,
                                'mediatype': 'show',
                                'genre': '%s'%genre,
                                'starttime': '%s'%gamestartepoch, 
                                'duration': '%s'%duration, 
                                'label': '%s'%sname, 
                                'label2': 'HD',
                                'channelname': '%s'%chname, 
                                'art': {
                                    'thumb': '%s'%chfanart,
                                     'fanart': '%s'%shthumb, 
                                     'poster': '', 
                                     'logo': '', 
                                     'clearart': '',
                                     'plot': '%s'%plot,
                                     'icon': '%s'%chlogo} 
                                    })
            chData['guidedata']=shData
            Guide_Data.append(chData)
        except: pass
    return Guide_Data
