# -*- coding: utf-8 -*-

"""
    Addon for genrating xml files from TMDB, IMDB, and Trakt list numbers
    Copyright (C) 2018, TonyH
    version 5.6.2

        - 6-28-20:  Re-wrote the addon
                    Added summary to xml's

        - 7-20-19:  Added Trailer option to settings
                    true will print a youtube trailer link in link position 1

        -- Thanks to Bugatsinho for the sorting code--

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

import os,sys,time,xbmc,xbmcaddon,xbmcgui,xbmcplugin
import requests,re,json,urllib

addon_id            = xbmcaddon.Addon().getAddonInfo('id')
dialog              = xbmcgui.Dialog()
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder,'addons')
addon_path          = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(addon_path, 'resources')
art_path            = os.path.join(resources_path, 'art')
userdata_folder     = os.path.join(home_folder,'userdata')
addon_data_folder   = os.path.join(userdata_folder,'addon_data')
xmlerator_data      = os.path.join(addon_data_folder,addon_id)
xml_path            = os.path.join(xmlerator_data, 'xmls')
ownAddon            = xbmcaddon.Addon(id=addon_id)  
tmdb_api_key        = ownAddon.getSetting('TMDB_api')
trakt_client_id     = ownAddon.getSetting('Trakt_api')
Text_color          = ownAddon.getSetting('Text_color')
bold_value          = ownAddon.getSetting('bold_type')
get_trailer         = ownAddon.getSetting("include_trailer")
json_output         = ownAddon.getSetting("json_out")
User_Agent          = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'

if os.path.exists(xmlerator_data): pass
else: os.mkdir(xmlerator_data, 0755) 
if os.path.exists(xml_path): pass
else: os.mkdir(xml_path, 0755) 

def start():
    addDir("Directions","directions",2,os.path.join(addon_path,'icon.png'),os.path.join(addon_path,'fanart.jpg'),"Directions")
    addDir("TMDB List","tmdb",3,os.path.join(art_path,'tmdb.png'),os.path.join(addon_path,'fanart.jpg'),"TMDB List")
    addDir("IMDB List","imdb",4,os.path.join(art_path,'imdb.png'),os.path.join(addon_path,'fanart.jpg'),"IMDB List")
    addDir("Trakt List","trakt",5,os.path.join(art_path,'trakt.png'),os.path.join(addon_path,'fanart.jpg'),"Trakt List")
    addDir("Settings","settings",6,os.path.join(art_path,'settings.png'),os.path.join(addon_path,'fanart.jpg'),"Settings")
    addDir("Sort xml by Year","year",7,os.path.join(addon_path,'icon.png'),os.path.join(addon_path,'fanart.jpg'),"Sort xml by Year")
    addDir("Sort xml by Title","title",7,os.path.join(addon_path,'icon.png'),os.path.join(addon_path,'fanart.jpg'),"Sort xml by Title")

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('fanart_image', fanart)
    if mode==2 or 6: ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    else: ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def directions():
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Directions', '1. Open the settings and enter your TMDB api key and, Trakt Client id.\n'
                                 'The TMDB api key is needed for ALL lists.\n'
                                 '\n'
                                 '2. Click on TMDB, IMDB, or Trakt Lists and you will be promted for a folder name.\n'
                                 'This will create a folder in the userdata/addon_data/plugin.program.xmlerator/xmls folder\n'
                                 'with the name that you chose, and the xmls will be created here.\n'
                                 '\n'
                                 '3. Enter your list number or list name in the dialog box.\n'
                                 'Trakt lists require a user name AND a matching list name.\n'
                                 'Both are in the url, example: https://trakt.tv/users/tony5856/lists/test-movies.\n'
                                 '\n'
                                 '4. The xmls will be created in your specified folder along with a txt file\n'
                                 'called missing_art. This is a list of the movies, tv shows, or episodes that\n'
                                 'did not return any artwork.\n'
                                 '\n'
                                 '5. Put the xmls on your host or local and link to them from your main.xml\n'
                                 '\n'
                                 '6. Tv shows in the generated xml will need to link to the location of\n'
                                 'the seasons xml for that show. The seasons xml will need to link to the location\n'
                                 'of the episodes xml.')

def Tmdb_info(url):
    Total = []
    dialog = xbmcgui.Dialog()
    if tmdb_api_key == 'TMDB':
        dialog.notification('Enter api key', 'Enter TMDB api key in settings', xbmcgui.NOTIFICATION_INFO, 5000)
        return
    trail_key = ""
    folder_name = output_folder()
    xml_folder = os.path.join(xml_path, folder_name)
    list_number = dialog.input('TMDB List Number')
    start_url = "https://api.themoviedb.org/3/list/%s?api_key=%s&language=en-US"% (int(list_number) ,tmdb_api_key)
    html = requests.get(start_url).content
    match = json.loads(html)
    list_name = match['name']
    list_name = list_name.replace(" ", "_")
    list_name = clean_search(list_name)
    if not list_name:
        list_name = match['description']
    res = match['items']
    if not res:
        res = match['results']
    xml_folder = os.path.join(xml_path, folder_name)
    File = os.path.join(xml_folder, list_name)
    length = len(res)
    count = 0
    dp = xbmcgui.DialogProgress()
    dp.create("[COLOR ghostwhite]Writing XML's....  [/COLOR]")       
    open('%s.xml'%(File),'w')
    for results in res:
        count = count + 1
        progress(length,count,dp)
        tmdb = results['id']
        media = results['media_type']
        if media == 'movie':
            eurl = "https://api.themoviedb.org/3/movie/%s/external_ids?api_key=%s"%(tmdb,tmdb_api_key)
            data = requests.get(eurl).json()
            imdb = data['imdb_id']
        elif media == 'tv':
            eurl = "https://api.themoviedb.org/3/tv/%s/external_ids?api_key=%s&language=en-US"%(tmdb,tmdb_api_key)
            data = requests.get(eurl).json()
            imdb = data['imdb_id']
        if json_output == 'true':
            movies = get_metadata(tmdb,imdb,media,folder_name,list_name)
            Total.append(movies)
        get_metadata(tmdb,imdb,media,folder_name,list_name)
    xml_folder = os.path.join(xml_path,folder_name)
    Test_file = os.path.join(xml_folder,'test')
    f = open('%s.json'%(Test_file), 'a')
    json.dump(Total,f,indent=4,sort_keys=True)
    f.close()


def imdb_info(url):
    dialog = xbmcgui.Dialog()
    if tmdb_api_key == 'TMDB':
        dialog.notification('Enter api key', 'Enter TMDB api key in settings', xbmcgui.NOTIFICATION_INFO, 5000)
        return
    folder_name = output_folder() 
    list_number2 = dialog.input('IMDB List Number')   
    list_number2 = list_number2.replace("ls", "")
    try:
        url = "http://www.imdb.com/list/ls%s/" % int(list_number2)
        html = requests.get(url).content
        match2 = re.compile('<h1 class="header list-name">(.+?)</h1>.+?<div class="desc lister-total-num-results">(.+?)</div>',re.DOTALL).findall(html)       
        for list_name, total_list in match2:
            list_name = clean_search(list_name)
            list_name = list_name.replace(" ", "_")
            total_list = total_list.replace("titles", "").replace(" ", "")
            length = int(total_list)
            count = 0
            dp = xbmcgui.DialogProgress()
            dp.create("[COLOR ghostwhite]Writing XML's....  [/COLOR]") 
            for x in range(1,15):
                url2 = "https://www.imdb.com/list/ls%s/?sort=list_order,asc&st_dt=&mode=detail&page=%s"%(list_number2,x)
                html2 = requests.get(url2).content
                block = re.compile('<div class="lister-list">(.+?)<div class="row text-center lister-working hidden"></div>',re.DOTALL).findall(html2)
                match = re.compile('<img alt=.+?data-tconst="(.+?)"',re.DOTALL).findall(str(block))
                for imdb in match:
                    count = count + 1
                    progress(length, count, dp)
                    try:
                        iurl = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=imdb_id"%(imdb,tmdb_api_key)               
                        ihtml = requests.get(iurl).json()
                        movie_results = ihtml['movie_results']
                        tv_results = ihtml['tv_results']
                        if movie_results:
                            media = "movie"
                            tmdb = ihtml['movie_results'][0]['id']
                        elif tv_results:
                            media = "tv"
                            tmdb = ihtml['tv_results'][0]['id']
                        get_metadata(tmdb,imdb,media,folder_name,list_name)
                    except: pass
    except: pass

def trakt_info(url):
    dialog = xbmcgui.Dialog()
    if tmdb_api_key == 'TMDB':
        dialog.notification('Enter api key', 'Enter TMDB api key in settings', xbmcgui.NOTIFICATION_INFO, 5000)
        return
    if trakt_client_id == 'TRAKT':
        dialog.notification('Enter client key', 'Enter Trakt client key in settings', xbmcgui.NOTIFICATION_INFO, 5000)
        return
    folder_name = output_folder()
    trakt_user_name = dialog.input('Trakt User Name')
    list_number3 = dialog.input('Trakt List Name')
    list_name = list_number3.replace(" ", "-")
    user = trakt_user_name.replace(" ", "-")
    try:
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': trakt_client_id}
        url1 = "https://api.trakt.tv/users/%s/lists/%s/" % (user, list_name)
        html1 = requests.get(url1,headers=headers).content
        match1 = json.loads(html1)
        length = match1['item_count']
        url = "https://api.trakt.tv/users/%s/lists/%s/items/" % (user, list_name)
        count = 0
        dp = xbmcgui.DialogProgress()
        dp.create("[COLOR ghostwhite]Writing XML's....  [/COLOR]")        
        if user == "user-name":
            print "no"
        else:      
            html = requests.get(url,headers=headers).json()
            for res in html:   
                media = res['type']
                count = count + 1
                progress(length,count,dp)                 
                if media == 'movie': info = res['movie']                                       
                elif media == 'show': info = res['show']                   
                ids = info['ids']
                imdb = ids['imdb']
                iurl = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=imdb_id"%(imdb,tmdb_api_key)               
                ihtml = requests.get(iurl).json()
                if media == 'movie': tmdb = ihtml['movie_results'][0]['id']
                elif media == 'show': tmdb = ihtml['tv_results'][0]['id']
                get_metadata(tmdb,imdb,media,folder_name,list_name)
    except: pass

def get_metadata(tmdb,imdb,media,folder_name,list_name):
    time.sleep(.2)
    icon        = ""
    fanart      = ""
    name        = ""
    year        = ""
    genre       = ""
    summary     = ""
    trail_key   = ""
    date        = ""
    if media == 'show': media = 'tv'
    base2 = "http://image.tmdb.org/t/p/w185"
    if media == 'movie':
        url = "https://api.themoviedb.org/3/movie/%s?api_key=%s&language=en-US"%(tmdb,tmdb_api_key)
        data = requests.get(url).json()
        name = data['original_title'].encode('utf-8')
        date = data['release_date']
        year = date.split("-")[0]
        fanart = data['backdrop_path']
        if not fanart:
            key = "fanart"
            show_name = ""
            missing_art(show_name,name,key,folder_name)
        genre = data['genres'][0]['name']
        summary = data['overview'].encode('utf-8')
        icon = data['poster_path']
        if not icon:
            key = "thumbnail"
            show_name = ""
            missing_art(show_name,name,key,folder_name)
        if get_trailer == 'true':
            try:
                turl = "https://api.themoviedb.org/3/movie/%s/videos?api_key=%s" % (tmdb, tmdb_api_key)
                thtml = requests.get(turl).json()
                r = thtml['results'][0]
                site = thtml['results'][0]['site']
                if site == "YouTube":                                   
                    trail_key = thtml['results'][0]['key']
            except: pass
    elif media == 'tv':
        url = "https://api.themoviedb.org/3/tv/%s?api_key=%s&language=en-US"%(tmdb,tmdb_api_key)
        data = requests.get(url).json()
        name = data['original_name'].encode('utf-8')
        icon = data['poster_path']
        if not icon:
            icon = ""
            key = "thumbnail"
            show_name = ""
            missing_art(show_name, name, key, folder_name)
        date = data['first_air_date']
        year = date.split("-")[0]
        summary = data['overview'].encode('utf-8')
        fanart = data['backdrop_path']
        if not fanart:
            fanart = ""
            key = "fanart"
            show_name = ""
            missing_art(show_name, name, key, folder_name)
        if get_trailer == 'true':
            try:
                turl = "https://api.themoviedb.org/3/tv/%s/videos?api_key=%s" % (tmdb, tmdb_api_key)
                thtml = requests.get(turl).json()
                r = thtml['results'][0]
                site = thtml['results'][0]['site']
                if site == "YouTube":                                   
                    trail_key = thtml['results'][0]['key']
            except: pass                    
        get_tv_seasons(tmdb, fanart, imdb, folder_name)
    if json_output == 'true':
        Movies = {'name':name, 'year':year, 'imdb':imdb, 'tmdb':tmdb,
                    'icon':icon, 'fanart':fanart, 'summary':summary}
        return Movies
        #print_movie_json(list_name, media, name, year, imdb, tmdb, icon, fanart, folder_name,trail_key,summary)
        
    # else:
    #     print_movie_xml(list_name, media, name, year, imdb, tmdb, icon, fanart, folder_name,trail_key,summary)


def open_settings():
    xbmcaddon.Addon().openSettings()

def print_movie_json(list_name, media, name, year, imdb, tmdb, icon, fanart, folder_name,trail_key,summary):
    if media == "movie":
        xml_folder = os.path.join(xml_path,folder_name)
        Test_file = os.path.join(xml_folder,'test')
        Movies = {'name':name, 'year':year, 'imdb':imdb, 'tmdb':tmdb,
                    'icon':icon, 'fanart':fanart, 'summary':summary}
        f = open('%s.json'%(Test_file), 'a')
        json.dump(Movies,f,indent=4,sort_keys=True)
        f.close()
        # with open('%s.json'%(Test_file), 'a',indent=4,sort_keys=True) as json_file:
        #     json.dump(Movies, json_file)


def print_movie_xml(list_name, media, name, year, imdb, tmdb, icon, fanart, folder_name,trail_key,summary):
    try:       
        if media == "movie":
            name = name.encode('utf-8')
            xml_folder = os.path.join(xml_path,folder_name)
            File = os.path.join(xml_folder,list_name)      
            f = open('%s.xml'%(File),'a')
            f.write('<item>\n')
            if bold_value == "true":
                f.write('\t<title>[B][COLOR=%s]%s[/COLOR][/B]</title>\n' % (Text_color,name))
            else:    
                f.write('\t<title>[COLOR=%s]%s[/COLOR]</title>\n' % (Text_color,name))
            f.write('\t<meta>\n')
            f.write('\t<imdb>%s</imdb>\n' % imdb)
            f.write('\t<content>%s</content>\n' % media)
            f.write('\t<title>%s</title>\n' % (name))
            f.write('\t<year>%s</year>\n' % year)
            f.write('\t</meta>\n')
            f.write('\t<link>\n')
            if trail_key != "":
                trail_key = "https://www.youtube.com/watch?v=%s&feature=youtu.be" % (trail_key)
                f.write('\t<sublink>%s(Trailer)</sublink>\n' % trail_key)    
            f.write('\t<sublink>%s</sublink>\n' % "search")
            f.write('\t<sublink>%s</sublink>\n' % "searchsd")
            f.write('\t</link>\n')
            f.write('\t<summary>%s</summary>\n' % summary)
            f.write('\t<thumbnail>https://image.tmdb.org/t/p/original%s</thumbnail>\n' % icon)
            f.write('\t<fanart>https://image.tmdb.org/t/p/original%s</fanart>\n' % fanart)
            f.write('</item>\n')
            f.close()   
        elif media == "tv":
            name = name.encode('utf-8')
            xml_folder = os.path.join(xml_path,folder_name)
            File = os.path.join(xml_folder,list_name)
            f = open('%s.xml'%(File),'a')
            f.write('<dir>\n')
            if bold_value == "true":
                f.write('\t<title>[B][COLOR=%s]%s[/COLOR][/B]</title>\n' % (Text_color,name))
            else:
                f.write('\t<title>[COLOR=%s]%s[/COLOR]</title>\n' % (Text_color,name))
            f.write('\t<meta>\n')
            f.write('\t<imdb>%s</imdb>\n' % imdb)
            f.write('\t<content>%s</content>\n' % media)
            f.write('\t<title>%s</title>\n' % (name))
            f.write('\t<year>%s</year>\n' % year)
            f.write('\t</meta>\n')
            f.write('\t<link>\n')
            if trail_key != "":
                trail_key = "https://www.youtube.com/watch?v=%s&feature=youtu.be" % (trail_key)
                f.write('\t<sublink>%s(Trailer)</sublink>\n' % trail_key)
            f.write('\t</link>\n')
            f.write('\t<summary>%s</summary>\n' % summary)    
            f.write('\t<thumbnail>https://image.tmdb.org/t/p/original%s</thumbnail>\n' % icon)
            f.write('\t<fanart>https://image.tmdb.org/t/p/original%s</fanart>\n' % fanart)
            f.write('</dir>\n')
            f.close()
    except:
        pass

def get_tv_seasons(tmdb, fanart, imdb, folder_name):
    try:
        summary = ""      
        url = "https://api.themoviedb.org/3/tv/%s?api_key=%s&language=en-US" % (tmdb, tmdb_api_key)
        html = requests.get(url).content
        match = json.loads(html)
        seas = match['seasons']
        show_name = match['original_name']
        show_name = show_name.replace(":", "")
        show_name = clean_search(show_name)
        xml_folder = os.path.join(xml_path, folder_name)
        File_show = os.path.join(xml_folder, show_name)
        open('%s.xml'%(File_show),'w')
        for seasons in seas:   
            sea_name = seasons['name'].encode('utf-8')
            date = seasons['air_date']
            summary = seasons['overview'].encode('utf-8')
            if not date:
                year = ""            
            else:
                year = date.split("-")[0]
            icon = seasons['poster_path']
            if not 'poster_path':
                key = "thumbnail"
                missing_art(show_name, sea_name, key, folder_name)
                icon = ""
            sea_num = seasons['season_number']
            if not sea_num:
                sea_num = ""
            get_episodes(tmdb, sea_num, fanart, sea_name, show_name, imdb, folder_name)
            print_seasons_xml(show_name, sea_name, year, fanart, icon, imdb, sea_num, folder_name,summary)

    except:
        pass

def get_episodes(tmdb, sea_num, fanart, sea_name, show_name, imdb, folder_name):
    try:
        summary = ""
        url = "https://api.themoviedb.org/3/tv/%s/season/%s?api_key=%s&language=en-US" % (tmdb, sea_num, tmdb_api_key)
        html = requests.get(url).content
        match = json.loads(html)
        episodes = match['episodes']
        Episodes = show_name+"_"+sea_name
        xml_folder = os.path.join(xml_path, folder_name)
        File_episode = os.path.join(xml_folder, Episodes)
        f = open('%s.xml' % File_episode, 'wb')
        for epi in episodes:
            name = epi['name'].encode('utf-8')
            summary = epi['overview'].encode('utf-8')
            episode_num = epi['episode_number']
            season_num = epi['season_number']
            icon = epi['still_path']
            if not icon:
                key = "thumbnail"
                missing_art(show_name, name, key, folder_name)
                icon = ""
            date = epi['air_date']
            if not date:
                year = ""            
            else:
                year = date.split("-")[0]
            print_episodes_xml(show_name, sea_name, fanart, name, season_num, episode_num, icon, year, imdb, folder_name,summary)
    except:
        pass

def print_seasons_xml(show_name, sea_name, year, fanart, icon, imdb, sea_num, folder_name,summary):
    try:
        xml_folder = os.path.join(xml_path, folder_name)
        File_show = os.path.join(xml_folder, show_name)
        f = open('%s.xml' % File_show,'a')
        f.write('<dir>\n')
        if bold_value == "true":
            f.write('\t<title>[B][COLOR=%s]%s[/COLOR][/B]</title>\n' % (Text_color, sea_name))
        else:
            f.write('\t<title>[COLOR=%s]%s[/COLOR]</title>\n' % (Text_color, sea_name))
        f.write('\t<meta>\n')
        f.write('\t<imdb>%s</imdb>\n' % imdb)
        f.write('\t<content>season</content>\n')
        f.write('\t<season>%s</season>\n' % sea_num)
        f.write('\t<year>%s</year>\n' % year)
        f.write('\t</meta>\n')
        f.write('\t<link></link>\n')
        f.write('\t<summary>%s</summary>\n' % summary)
        f.write('\t<thumbnail>https://image.tmdb.org/t/p/original%s</thumbnail>\n' % icon)
        f.write('\t<fanart>https://image.tmdb.org/t/p/original%s</fanart>\n' % fanart)
        f.write('</dir>\n')
        f.close()   
    except:
        pass

def print_episodes_xml(show_name, sea_name, fanart, name, season_num, episode_num, icon, year, imdb, folder_name,summary):
    try:        
        Episodes = show_name + "_" + sea_name
        xml_folder = os.path.join(xml_path ,folder_name)
        File_episode = os.path.join(xml_folder, Episodes)
        f = open('%s.xml' % File_episode, 'a')
        f.write('<item>\n')
        if bold_value == "true":
            f.write('\t<title>[B][COLOR=%s]%s[/COLOR][/B]</title>\n' % (Text_color, name))
        else:
            f.write('\t<title>[COLOR=%s]%s[/COLOR]</title>\n' % (Text_color, name))
        f.write('\t<meta>\n')
        f.write('\t<imdb>%s</imdb>\n' % imdb)
        f.write('\t<content>episode</content>\n')
        f.write('\t<tvshowtitle>%s</tvshowtitle>\n' % show_name)
        f.write('\t<year>%s</year>\n' % year)
        f.write('\t<season>%s</season>\n' % season_num)
        f.write('\t<episode>%s</episode>\n' % episode_num)
        f.write('\t</meta>\n')
        f.write('\t<link>\n')
        f.write('\t<sublink>search</sublink>\n')
        f.write('\t<sublink>searchsd</sublink>\n')
        f.write('\t</link>\n')
        f.write('\t<summary>%s</summary>\n' % summary)
        f.write('\t<thumbnail>https://image.tmdb.org/t/p/original%s</thumbnail>\n' % icon)
        f.write('\t<fanart>https://image.tmdb.org/t/p/original%s</fanart>\n' % fanart)
        f.write('</item>\n')
        f.close()
    except:
        pass

def sort_xml(url):
    dg = xbmcgui.Dialog()
    selected = dg.browse(1, 'Select XML', 'files', '.xml', False, False, xml_path, False)
    with open(selected, 'rb') as xml:
        from dom_parser import parseDOM as dom
        read = xml.read()
        items = dom(read, 'item')
        final = ''
        if 'year' in url:
            head1 = '[B][COLORgold]Select Sorting Method[/COLOR][/B]'
            head2 = '[COLORgold]NEWEST to OLDEST[/COLOR]'
            head3 = '[COLORgold]OLDEST to NEWEST[/COLOR]'
            ret = dg.select(head1, [head2, head3])
            if ret == -1:
                return
            elif ret == 0:
                rev = True
                xml_name = '_newtoold_year.xml'
            else:
                rev = False
                xml_name = '_oldtonew_year.xml'
            sort_items = sorted(items, key=lambda item: dom(item, 'year'), reverse=rev)

            with open(selected[:-4] + xml_name, 'wb') as f:
                for item in sort_items:
                    final += '<item>\n\t' + item + '\n</item>\n'
                f.write(final)
                f.close()
            xml.close()
            xbmcgui.Dialog().ok('XMLerator', 'NEW SORTED XML CREATED', '', '')
        else:
            sort_items = sorted(items, key=lambda item: dom(item, 'title'), reverse=False)
            with open(selected[:-4] + '_title_sorted.xml', 'wb') as f:
                for item in sort_items:
                    final += '<item>\n\t' + item + '\n</item>\n'
                f.write(final)
                f.close()
            xml.close()
            xbmcgui.Dialog().ok('XMLerator', 'NEW SORTED XML CREATED', '', '')

def clean_search(title):
    if title == None: return
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|/|\(|\)|\[|\]|\{|\}|-|:|;|\*|\?|"|\'|<|>|\_|\.|\?', ' ', title)
    title = title.replace(":", "")
    title = title.replace("xc2","")
    title = title.replace("xb7","")
    title = title.replace("\\","")    
    title = ' '.join(title.split())
    return title

def output_folder():
    dialog      = xbmcgui.Dialog()
    folder_name = dialog.input('Output Folder Name')
    folder_name = folder_name.replace(" ", "_")
    xml_folder  = os.path.join(xml_path, folder_name)
    if os.path.exists(xml_folder):
        dialog.notification('Folder Already Exists', 'Choose a different folder name', xbmcgui.NOTIFICATION_INFO, 5000)
        xml_folder = output_folder()
    else:
        os.mkdir(xml_folder, 0755)
        return folder_name    


def progress(length, count, dp):
    try:
        percent = (count * 100) / length
        if dp.iscanceled():
            dp.close()
            raise Exception("Cancelled")
        else:
            dp.update(percent, "%s of %s written" % (count, length))
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled():
        dp.close()
        raise Exception("Canceled")

def missing_art(show_name, name, key, folder_name):
    missing_art = 'missing_art'
    xml_folder = os.path.join(xml_path, folder_name)
    File_missing_art = os.path.join(xml_folder, missing_art)
    f = open('%s.txt' % File_missing_art, 'a')
    if show_name == "":
        f.write('Movie : '+name+' - missing - '+key+'\n')
    else:
        f.write('TV Show : '+show_name+' : '+name+' - missing - '+key+'\n')
    f.close()

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
    directions()
elif mode==3:
    Tmdb_info(url)
elif mode==4:
    imdb_info(url)
elif mode==5:
    trakt_info(url)
elif mode==6:
    open_settings()
elif mode==7:
    sort_xml(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))