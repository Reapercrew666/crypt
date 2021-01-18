# -*- coding: utf-8 -*-

"""
    Copyright (C) 2020, TonyH

    Module for the pluto2tv addon
    for context menu epg json_data

"""

import requests,re,json,koding,urllib,urllib2,uuid,xbmc,xbmcaddon
import sys
from datetime import timedelta
import datetime, time
from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal

#######################################
# Time and Date Helpers
#######################################
try:
    local_tzinfo = tzlocal()
    locale_timezone = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.timezone"}, "id": 1}'))
    if locale_timezone['result']['value']:
        local_tzinfo = gettz(locale_timezone['result']['value'])
except:
    pass

def convDateUtil(timestring, newfrmt='default', in_zone='UTC'):
    if newfrmt == 'default':
        newfrmt = xbmc.getRegion('time').replace(':%S','')
    try:
        in_time = parse(timestring)
        in_time_with_timezone = in_time.replace(tzinfo=gettz(in_zone))
        local_time = in_time_with_timezone.astimezone(local_tzinfo)
        return local_time.strftime(newfrmt)
    except:
        return timestring


sid1 = str(uuid.uuid1())
deviceId1 = str(uuid.uuid4())
BASE_API     = 'https://api.pluto.tv'
BASE_GUIDE   = BASE_API + '/v2/channels?start=%s&stop=%s&%s'

def timezone():
    if time.localtime(time.time()).tm_isdst and time.daylight: return time.altzone / -(60*60) * 100
    else: return time.timezone / -(60*60) * 100

def results():
    tz    = str(timezone())
    start = datetime.datetime.now().strftime('%Y-%m-%dT%H:00:00').replace('T','%20').replace(':00:00','%3A00%3A00.000'+tz)
    stop  = (datetime.datetime.now() + datetime.timedelta(hours=12)).strftime('%Y-%m-%dT%H:00:00').replace('T','%20').replace(':00:00','%3A00%3A00.000'+tz)
    return (BASE_GUIDE %(start,stop,'sid=%s&deviceId=%s'%(sid1,deviceId1)))

def get_params():
    param=[]
    paramstring=sys.argv[1]
    if len(paramstring)>=2:
        params=sys.argv[1]
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

params=get_params()
name=None
total = ""
times =[]

try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
koding.Show_Busy(status=True)
url = results()
json_data = requests.get(url).json()
for res in json_data:
    wname = res['name']
    try: logo = res['logo']['path']
    except: logo = ""
    shows = res['timelines']
    if wname.lower() == name.lower():
        for t in shows:
            start = str(t['start'][0:19])
            fstart = datetime.datetime(*(time.strptime(start, "%Y-%m-%dT%H:%M:%S")[0:6])) + datetime.timedelta(hours=-8)
            (gstart1) = convDateUtil(fstart, 'default', 'Europe/Athens')
            gstart = datetime.datetime.strftime(gstart1,"%I:%M%p")
            stop = str(t['stop'][0:19])
            fstop = datetime.datetime(*(time.strptime(stop, "%Y-%m-%dT%H:%M:%S")[0:6])) + datetime.timedelta(hours=-8)
            (gstop1) = convDateUtil(fstop, 'default', 'Europe/Athens')
            gstop = datetime.datetime.strftime(gstop1,"%I:%M%p")
            sname = t['title'][0:71]
            info = sname+"     "+gstart+" - "+gstop
            times.append(info)
total =  '\n'.join(word for word in times).encode('utf-8')
koding.Show_Busy(status=False)
koding.Text_Box('%s program Info'%name,'%s'%total)
