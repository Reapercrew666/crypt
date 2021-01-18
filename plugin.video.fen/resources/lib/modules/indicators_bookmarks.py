import xbmc, xbmcgui, xbmcplugin
import os
from datetime import datetime, date
import json
from caches.trakt_cache import clear_trakt_watched_data, clear_trakt_collection_watchlist_data
from modules.utils import local_string as ls
from modules.utils import to_unicode, adjusted_datetime
from modules import settings
try: from sqlite3 import dbapi2 as database
except ImportError: from pysqlite2 import dbapi2 as database
# from modules.utils import logger

WATCHED_DB = xbmc.translatePath('special://profile/addon_data/plugin.video.fen/watched_status.db')

window = xbmcgui.Window(10000)

def get_resumetime(db_type, tmdb_id, season='', episode=''):
	try: resumetime = str((int(round(float(detect_bookmark(db_type, tmdb_id, season, episode)[0])))/float(100))*2400)
	except: resumetime = '0'
	return resumetime

def get_progress_percent(resumetime, duration):
	try: percent = str(int(round(float(resumetime)/duration*100)))
	except: percent = '0'
	return percent

def set_bookmark(db_type, media_id, curr_time, total_time, season='', episode=''):
	settings.check_database(WATCHED_DB)
	erase_bookmark(db_type, media_id, season, episode)
	adjusted_current_time = float(curr_time) - 5
	resume_point = round(adjusted_current_time/float(total_time)*100,1)
	dbcon = database.connect(WATCHED_DB)
	dbcur = dbcon.cursor()
	dbcur.execute("INSERT INTO progress VALUES (?, ?, ?, ?, ?, ?)", (db_type, media_id, season, episode, str(resume_point), str(curr_time)))
	dbcon.commit()
	if settings.sync_kodi_library_watchstatus():
		from modules.kodi_library import set_bookmark_kodi_library
		set_bookmark_kodi_library(db_type, media_id, curr_time, total_time, season, episode)

def detect_bookmark(db_type, media_id, season='', episode=''):
	settings.check_database(WATCHED_DB)
	dbcon = database.connect(WATCHED_DB)
	dbcon.row_factory = database.Row
	dbcur = dbcon.cursor()
	dbcur.execute("SELECT * FROM progress WHERE (db_type = ? and media_id = ? and season = ? and episode = ?)", (db_type, media_id, season, episode))
	for row in dbcur:
		resume_point = row['resume_point']
		curr_time = row['curr_time']
	return resume_point, curr_time

def erase_bookmark(db_type, media_id, season='', episode='', refresh='false'):
	settings.check_database(WATCHED_DB)
	dbcon = database.connect(WATCHED_DB)
	dbcur = dbcon.cursor()
	dbcur.execute("DELETE FROM progress where db_type=? and media_id=? and season = ? and episode = ?", (db_type, media_id, season, episode))
	dbcon.commit()
	refresh_container(refresh)

def get_watched_info_tv():
	info = []
	use_trakt = False
	try:
		if settings.watched_indicators() in (1, 2):
			from apis.trakt_api import trakt_indicators_tv
			use_trakt = True
			info = trakt_indicators_tv()
		else:
			use_trakt = False
			settings.check_database(WATCHED_DB)
			dbcon = database.connect(WATCHED_DB)
			dbcur = dbcon.cursor()
			dbcur.execute("SELECT media_id, season, episode, title, last_played FROM watched_status WHERE db_type = ?", ('episode',))
			info = dbcur.fetchall()
			dbcon.close()
	except: pass
	return info, use_trakt

def get_watched_info_movie():
	info = []
	use_trakt = False
	try:
		if settings.watched_indicators() in (1, 2):
			from apis.trakt_api import trakt_indicators_movies
			use_trakt = True
			info = trakt_indicators_movies()
		else:
			use_trakt = False
			settings.check_database(WATCHED_DB)
			dbcon = database.connect(WATCHED_DB)
			dbcur = dbcon.cursor()
			dbcur.execute("SELECT media_id, title, last_played FROM watched_status WHERE db_type = ?", ('movie',))
			info = dbcur.fetchall()
			dbcon.close()
	except: pass
	return info, use_trakt

def get_watched_status(watched_info, use_trakt, db_type, media_id, season='', episode=''):
	try:
		if use_trakt:
			if db_type == 'movie':
				watched = [i for i in watched_info if i[0] == media_id]
				if watched: return 1, 5
				return 0, 4
			else:
				watched = [i[2] for i in watched_info if i[0] == media_id]
				if watched:
					watched = [i for i in watched[0] if i[0] == season and i[1] == episode]
					if watched: return 1, 5
				return 0, 4
		else:
			if db_type == 'movie':
				watched = [i for i in watched_info if str(i[0]) == str(media_id)]
				if watched: return 1, 5
				return 0, 4
			else:
				watched = [i for i in watched_info if str(i[0]) == str(media_id) and (i[1],i[2]) == (season,episode)]
			if watched: return 1, 5
			else: return 0, 4
	except: return 0, 4

def get_watched_status_tvshow(watched_info, use_trakt, media_id, aired_eps):
	def get_playcount_overlay():
		playcount, overlay = 0, 4
		try:
			if use_trakt:
				watched = [i for i in watched_info if i[0] == media_id and i[1] == len(i[2])]
				if watched:
					playcount, overlay = 1, 5
			else:
				watched_list = [str(i[0]) for i in watched_info]
				watched = len([i for i in watched_list if i == str(media_id)])
				if watched == aired_eps and not aired_eps == 0:
					playcount, overlay = 1, 5
		except: pass
		return playcount, overlay
	def get_watched_episode_totals():
		watched, unwatched = 0, aired_eps
		try:
			if use_trakt:
				watched = len([i[2] for i in watched_info if i[0] == media_id][0])
				unwatched = [i[1] for i in watched_info if i[0] == media_id][0] - watched 
			else:
				watched_list = [str(i[0]) for i in watched_info]
				watched = len([i for i in watched_list if i == str(media_id)])
				unwatched = aired_eps - watched
		except: pass
		return watched, unwatched
	watched, unwatched = get_watched_episode_totals()
	playcount, overlay = get_playcount_overlay()
	return playcount, overlay, watched, unwatched

def get_watched_status_season(watched_info, use_trakt, media_id, season, aired_eps):
	def get_playcount_overlay(use_trakt):
		playcount, overlay = 0, 4
		try:
			if use_trakt:
				watched = [i[2] for i in watched_info if i[0] == media_id]
				if watched:
					if len([i for i in watched[0] if i[0] == season]) >= aired_eps:
						playcount, overlay = 1, 5
			else:
				watched = len([i for i in watched_info if str(i[0]) == str(media_id) and i[1] == season])
				if watched >= aired_eps and not aired_eps == 0:
					playcount, overlay = 1, 5
		except: pass
		return playcount, overlay
	def get_watched_episode_totals(use_trakt):
		watched, unwatched = 0, aired_eps
		try:
			if use_trakt:
				watched = [i[2] for i in watched_info if i[0] == media_id]
				if watched:
					watched = len([i for i in watched[0] if i[0] == season])
				else: watched = 0
				unwatched = aired_eps - watched
			else:
				watched = len([i for i in watched_info if str(i[0]) == str(media_id) and i[1] == season])
				unwatched = aired_eps - watched
		except: pass
		return watched, unwatched
	watched, unwatched = get_watched_episode_totals(use_trakt)
	playcount, overlay = get_playcount_overlay(use_trakt)
	return playcount, overlay, watched, unwatched

def get_watched_items(db_type, page_no, letter):
	from modules.nav_utils import paginate_list
	from modules.utils import title_key, to_utf8
	watched_indicators = settings.watched_indicators()
	ignore_articles = settings.ignore_articles()
	paginate = settings.paginate()
	limit = settings.page_limit()
	if db_type == 'tvshow':
		if watched_indicators in (1, 2):
			from apis.trakt_api import trakt_indicators_tv
			data = trakt_indicators_tv()
			data = sorted(data, key=lambda tup: title_key(tup[3], ignore_articles))
			original_list = [{'media_id': i[0], 'title': i[3], 'last_played': i[4]} for i in data if i[1] == len(i[2])]
		else:
			import metadata
			meta_user_info = metadata.retrieve_user_info()
			settings.check_database(WATCHED_DB)
			dbcon = database.connect(WATCHED_DB)
			dbcur = dbcon.cursor()
			dbcur.execute("SELECT media_id, title, last_played FROM watched_status WHERE db_type = ?", ('episode',))
			rows = dbcur.fetchall()
			dbcon.close()
			watched_list = list(set(to_utf8([(i[0], i[1], i[2]) for i in rows])))
			watched_info, use_trakt = get_watched_info_tv()
			data = []
			for item in watched_list:
				meta = metadata.tvshow_meta('tmdb_id', item[0], meta_user_info)
				watched = get_watched_status_tvshow(watched_info, use_trakt, item[0], meta.get('total_episodes'))
				if watched[0] == 1: data.append(item)
				else: pass
			data = sorted(data, key=lambda tup: title_key(tup[1]))
			original_list = [{'media_id': i[0], 'title': i[1], 'last_played': i[2]} for i in data]
	else:
		if watched_indicators in (1, 2):
			from apis.trakt_api import trakt_indicators_movies
			data = trakt_indicators_movies()
			data = sorted(data, key=lambda tup: title_key(tup[1]))
			original_list = [{'media_id': i[0], 'title': i[1], 'last_played': i[2]} for i in data]
			
		else:
			settings.check_database(WATCHED_DB)
			dbcon = database.connect(WATCHED_DB)
			dbcur = dbcon.cursor()
			dbcur.execute("SELECT media_id, title, last_played FROM watched_status WHERE db_type = ?", (db_type,))
			rows = dbcur.fetchall()
			dbcon.close()
			data = to_utf8([(i[0], i[1], i[2]) for i in rows])
			data = sorted(data, key=lambda tup: title_key(tup[1]))
			original_list = [{'media_id': i[0], 'title': i[1], 'last_played': i[2]} for i in data]
	if paginate: final_list, total_pages = paginate_list(original_list, page_no, letter, limit)
	else: final_list, total_pages = original_list, 1
	return final_list, total_pages

def mark_episode_as_watched_unwatched(params):
	from indexers.next_episode import add_next_episode_unwatched
	action = 'mark_as_watched' if params.get('action') == 'mark_as_watched' else 'mark_as_unwatched'
	media_id = params.get('media_id')
	tvdb_id = int(params.get('tvdb_id', '0'))
	imdb_id = params.get('imdb_id')
	season = int(params.get('season'))
	episode = int(params.get('episode'))
	title = params.get('title')
	year = params.get('year')
	refresh = params.get('refresh', 'true')
	from_playback = params.get('from_playback', 'false')
	watched_indicators = settings.watched_indicators()
	if season == 0:
		from modules.nav_utils import notification
		notification(ls(32490)); return
	if watched_indicators in (1, 2):
		import time
		from apis.trakt_api import trakt_watched_unwatched, trakt_official_status
		if from_playback == 'true'and trakt_official_status('episode') == False: skip_trakt_mark = True
		else: skip_trakt_mark = False
		if not skip_trakt_mark: trakt_watched_unwatched(action, 'episode', imdb_id, tvdb_id, season, episode)
		if skip_trakt_mark: time.sleep(3)
		clear_trakt_watched_data('tvshow')
		clear_trakt_collection_watchlist_data('watchlist', 'tvshow')
	if watched_indicators in (0, 1):
		mark_as_watched_unwatched('episode', media_id, action, season, episode, title)
	erase_bookmark('episode', media_id, season, episode)
	if action == 'mark_as_watched': add_next_episode_unwatched('remove', media_id, silent=True)
	if settings.sync_kodi_library_watchstatus():
		from modules.kodi_library import mark_as_watched_unwatched_kodi_library
		mark_as_watched_unwatched_kodi_library('episode', action, title, year, season, episode)
	refresh_container(refresh)

def mark_season_as_watched_unwatched(params):
	from indexers.next_episode import add_next_episode_unwatched
	action = 'mark_as_watched' if params.get('action') == 'mark_as_watched' else 'mark_as_unwatched'
	season = int(params.get('season'))
	title = params.get('title')
	year = params.get('year')
	media_id = params.get('media_id')
	tvdb_id = int(params.get('tvdb_id', '0'))
	imdb_id = params.get('imdb_id')
	watched_indicators = settings.watched_indicators()
	sync_kodi_library = settings.sync_kodi_library_watchstatus()
	if season == 0:
		from modules.nav_utils import notification
		notification(ls(32490)); return
	if watched_indicators in (1, 2):
		from apis.trakt_api import trakt_watched_unwatched
		trakt_watched_unwatched(action, 'season', imdb_id, tvdb_id, season)
		clear_trakt_watched_data('tvshow')
		clear_trakt_collection_watchlist_data('watchlist', 'tvshow')
		if sync_kodi_library:
			import metadata
			try: meta_user_info = json.loads(params.get('meta_user_info', ))
			except: meta_user_info = fmeta.retrieve_user_info()
			meta = metadata.tvshow_meta('tmdb_id', media_id, meta_user_info)
			ep_data = metadata.season_episodes_meta(media_id, tvdb_id, season, meta['tvdb_summary']['airedSeasons'], meta['season_data'], meta_user_info)
			se_list = []
			for item in ep_data:
				season_number = item['season']
				ep_number = item['episode']
				season_ep = '%.2d<>%.2d' % (season_number, ep_number)
				se_list.append(season_ep)
	if watched_indicators in (0, 1):
		import metadata
		bg_dialog = xbmcgui.DialogProgressBG()
		bg_dialog.create(ls(32577), '')
		try: meta_user_info = json.loads(params.get('meta_user_info', ))
		except: meta_user_info = metadata.retrieve_user_info()
		meta = metadata.tvshow_meta('tmdb_id', media_id, meta_user_info)
		ep_data = metadata.season_episodes_meta(media_id, tvdb_id, season, meta['tvdb_summary']['airedSeasons'], meta['season_data'], meta_user_info)
		count = 1
		se_list = []
		for item in ep_data:
			season_number = item['season']
			ep_number = item['episode']
			season_ep = '%.2d<>%.2d' % (season_number, ep_number)
			display = 'S%.2dE%.2d' % (season_number, ep_number)
			try:
				first_aired = item['premiered']
				d = first_aired.split('-')
				episode_date = date(int(d[0]), int(d[1]), int(d[2]))
			except: episode_date = date(2100,10,24)
			if not adjusted_datetime() > episode_date: continue
			bg_dialog.update(int(float(count) / float(len(ep_data)) * 100), ls(32577), '%s' % display)
			count += 1
			mark_as_watched_unwatched('episode', media_id, action, season_number, ep_number, title)
			se_list.append(season_ep)
		bg_dialog.close()
	if action == 'mark_as_watched': add_next_episode_unwatched('remove', media_id, silent=True)
	if sync_kodi_library:
		from modules.kodi_library import get_library_video, batch_mark_episodes_as_watched_unwatched_kodi_library
		in_library = get_library_video('tvshow', title, year)
		if not in_library: refresh_container(); return
		ep_dict = {'action': action, 'tvshowid': in_library['tvshowid'], 'season_ep_list': se_list}
		if batch_mark_episodes_as_watched_unwatched_kodi_library(in_library, ep_dict):
			from modules.nav_utils import notification
			notification(ls(32787), time=5000)
	refresh_container()

def mark_tv_show_as_watched_unwatched(params):
	from indexers.next_episode import add_next_episode_unwatched
	action = 'mark_as_watched' if params.get('action') == 'mark_as_watched' else 'mark_as_unwatched'
	media_id = params.get('media_id')
	tvdb_id = int(params.get('tvdb_id', '0'))
	imdb_id = params.get('imdb_id')
	watched_indicators = settings.watched_indicators()
	sync_kodi_library = settings.sync_kodi_library_watchstatus()
	if watched_indicators in (1, 2):
		from apis.trakt_api import trakt_watched_unwatched
		trakt_watched_unwatched(action, 'shows', imdb_id, tvdb_id)
		clear_trakt_watched_data('tvshow')
		clear_trakt_collection_watchlist_data('watchlist', 'tvshow')
		if sync_kodi_library:
			import metadata
			title = params.get('title', '')
			year = params.get('year', '')
			try: meta_user_info = json.loads(params.get('meta_user_info', ))
			except: meta_user_info = metadata.retrieve_user_info()
			se_list = []
			meta = metadata.tvshow_meta('tmdb_id', media_id, meta_user_info)
			season_data  = metadata.all_episodes_meta(media_id, tvdb_id, meta['tvdb_summary']['airedSeasons'], meta['season_data'], meta_user_info)
			for item in season_data:
				season_number = item['season_number']
				if season_number <= 0: continue
				ep_data = metadata.season_episodes_meta(media_id, tvdb_id, season_number, meta['tvdb_summary']['airedSeasons'], meta['season_data'], meta_user_info)
				for ep in ep_data:
					season_number = ep['season']
					ep_number = ep['episode']
					season_ep = '%.2d<>%.2d' % (int(season_number), int(ep_number))
					se_list.append(season_ep)
	if watched_indicators in (0, 1):
		import metadata
		bg_dialog = xbmcgui.DialogProgressBG()
		bg_dialog.create(ls(32577), '')
		title = params.get('title', '')
		year = params.get('year', '')
		try: meta_user_info = json.loads(params.get('meta_user_info', ))
		except: meta_user_info = metadata.retrieve_user_info()
		se_list = []
		count = 1
		meta = metadata.tvshow_meta('tmdb_id', media_id, meta_user_info)
		season_data  = metadata.all_episodes_meta(media_id, tvdb_id, meta['tvdb_summary']['airedSeasons'], meta['season_data'], meta_user_info)
		total = sum([i['episode_count'] for i in season_data if i['season_number'] > 0])
		for item in season_data:
			season_number = item['season_number']
			if season_number <= 0: continue
			ep_data = metadata.season_episodes_meta(media_id, tvdb_id, season_number, meta['tvdb_summary']['airedSeasons'], meta['season_data'], meta_user_info)
			for ep in ep_data:
				season_number = ep['season']
				ep_number = ep['episode']
				season_ep = '%.2d<>%.2d' % (int(season_number), int(ep_number))
				display = 'S%.2dE%.2d' % (int(season_number), int(ep_number))
				bg_dialog.update(int(float(count)/float(total)*100), 'Please Wait', '%s' % display)
				count += 1
				try:
					first_aired = ep['premiered']
					d = first_aired.split('-')
					episode_date = date(int(d[0]), int(d[1]), int(d[2]))
				except: episode_date = date(2100,10,24)
				if not adjusted_datetime() > episode_date: continue
				mark_as_watched_unwatched('episode', media_id, action, season_number, ep_number, title)
				se_list.append(season_ep)
		bg_dialog.close()
	if action == 'mark_as_watched': add_next_episode_unwatched('remove', media_id, silent=True)
	if sync_kodi_library:
		from modules.kodi_library import get_library_video, batch_mark_episodes_as_watched_unwatched_kodi_library
		in_library = get_library_video('tvshow', title, year)
		if not in_library: refresh_container(); return
		if not in_library: return
		from modules.nav_utils import notification
		ep_dict = {'action': action, 'tvshowid': in_library['tvshowid'], 'season_ep_list': se_list}
		if batch_mark_episodes_as_watched_unwatched_kodi_library(in_library, ep_dict):
			notification(ls(32787), time=5000)
	refresh_container()

def mark_movie_as_watched_unwatched(params):
	action = params.get('action')
	db_type = 'movie'
	media_id = params.get('media_id')
	title = params.get('title')
	year = params.get('year')
	refresh = params.get('refresh', 'true')
	watched_indicators = settings.watched_indicators()
	if watched_indicators in (1, 2):
		from apis.trakt_api import trakt_watched_unwatched
		trakt_watched_unwatched(action, 'movies', media_id)
		clear_trakt_watched_data(db_type)
		clear_trakt_collection_watchlist_data('watchlist', 'movie')
	if watched_indicators in (0, 1):
		mark_as_watched_unwatched(db_type, media_id, action, title=title)
	erase_bookmark(db_type, media_id)
	if settings.sync_kodi_library_watchstatus():
		from modules.kodi_library import mark_as_watched_unwatched_kodi_library
		mark_as_watched_unwatched_kodi_library(db_type, action, title, year)
	refresh_container()

def mark_as_watched_unwatched(db_type='', media_id='', action='', season='', episode='', title=''):
	try:
		settings.check_database(WATCHED_DB)
		last_played = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		dbcon = database.connect(WATCHED_DB, timeout=40.0)
		erase_bookmark(db_type, media_id, season, episode)
		if action == 'mark_as_watched':
			dbcon.execute("INSERT OR IGNORE INTO watched_status VALUES (?, ?, ?, ?, ?, ?)", (db_type, media_id, season, episode, last_played, to_unicode(title)))
		elif action == 'mark_as_unwatched':
			dbcon.execute("DELETE FROM watched_status WHERE (db_type = ? and media_id = ? and season = ? and episode = ?)", (db_type, media_id, season, episode))
		dbcon.commit()
	except:
		from modules.nav_utils import notification
		notification(ls(32574))

def refresh_container(refresh='true'):
	if refresh == 'true': xbmc.executebuiltin("Container.Refresh")

