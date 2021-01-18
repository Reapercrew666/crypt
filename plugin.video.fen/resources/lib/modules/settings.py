import xbmc
from modules.settings_reader import get_setting
# from modules.utils import logger

def addon():
	from xbmcaddon import Addon
	return Addon(id='plugin.video.fen')

def ext_addon(addon_id):
	from xbmcaddon import Addon
	return Addon(id=addon_id)

def addon_installed(addon_id):
	if xbmc.getCondVisibility('System.HasAddon(%s)' % addon_id): return True
	else: return False

def get_theme():
	theme = 'light' if get_setting('fen.theme') in ('0', '-', '') else 'heavy'
	return xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/media/%s' % theme)

def skin_location():
	return xbmc.translatePath('special://home/addons/script.module.tikiskins')

def results_xml_style():
	return str(get_setting('results.xml_style', 'List Default').lower())

def results_xml_window_number(window_style=None):
	if not window_style: window_style = results_xml_style()
	return 2000 if window_style.startswith('list') else 2001#shift

def tmdb_api_check():
	return '1b0d3c6ac6a6c0fa87b55a1069d6c9c8'

def check_database(database):
	import xbmcvfs
	if not xbmcvfs.exists(database): initialize_databases()

def store_resolved_torrent_to_cloud(debrid_service):
	return get_setting('store_torrent.%s' % debrid_service.lower()) == 'true'

def debrid_enabled(debrid_service):
	enabled = get_setting('%s.enabled' % debrid_service) == 'true'
	if not enabled: return False
	authed = get_setting('%s.token' % debrid_service)
	if authed not in (None, ''): return True
	return False

def debrid_priority(debrid_service):
	return int(get_setting('%s.priority' % debrid_service, '10'))

def display_sleep_time():
	return 0.1

def show_specials():
	return get_setting('show_specials') == 'true'

def auto_start_fen():
	return get_setting('auto_start_fen') == 'true'

def setview_delay():
	return float(int(get_setting('setview_delay', '800')))/1000
	
def movies_directory():
	return xbmc.translatePath(get_setting('movies_directory'))
	
def tv_show_directory():
	return xbmc.translatePath(get_setting('tv_shows_directory'))

def download_directory(db_type):
	setting = 'movie_download_directory' if db_type == 'movie' \
		else 'tvshow_download_directory' if db_type == 'episode' \
		else 'image_download_directory' if db_type == 'image' \
		else 'premium_download_directory'
	if get_setting(setting) != '': return xbmc.translatePath(get_setting(setting))
	else: return False

def source_folders_directory(db_type, source):
	setting = '%s.movies_directory' % source if db_type == 'movie' else '%s.tv_shows_directory' % source
	if get_setting(setting) not in ('', 'None', None): return xbmc.translatePath( get_setting(setting))
	else: return False

def paginate():
	return get_setting('paginate.lists') == "true"

def page_limit():
	return int(get_setting('page_limit', '20'))

def ignore_articles():
	return get_setting('ignore_articles') == "true"

def default_all_episodes():
	return int(get_setting('default_all_episodes'))

def quality_filter(setting):
	return get_setting(setting).split(', ')

def include_prerelease_results():
	return get_setting('include_prerelease_results') == "true"

def include_sources_in_filter(source_setting):
	return get_setting('%s_in_filter' % source_setting) == "true"

def auto_play():
	return get_setting('auto_play') == "true"

def autoplay_next_episode():
	if auto_play() and get_setting('autoplay_next_episode') == "true": return True
	else: return False

def autoplay_next_check_threshold():
	return int(get_setting('autoplay_next_check_threshold', '3'))

def filter_hevc():
	return int(get_setting('filter_hevc', '0'))

def sync_kodi_library_watchstatus():
	return get_setting('sync_kodi_library_watchstatus') == "true"

def refresh_trakt_on_startup():
	return get_setting('refresh_trakt_on_startup') == "true"
	
def trakt_cache_duration():
	duration = (1, 24, 168)
	return duration[int(get_setting('trakt_cache_duration'))]

def calendar_focus_today():
	return get_setting('calendar_focus_today') == 'true'

def watched_indicators():
	if get_setting('trakt_user') == '': return 0
	watched_indicators = get_setting('watched_indicators')
	if watched_indicators == '0': return 0
	if watched_indicators == '1' and get_setting('sync_fen_watchstatus') == 'true': return 1
	return 2

def sync_fen_watchstatus():
	if get_setting('sync_fen_watchstatus') == 'false': return False
	if get_setting('trakt_user') == '': return False
	if watched_indicators() in (0, 2): return False
	return True

def check_prescrape_sources(scraper):
	if scraper in ('furk', 'easynews', 'rd-cloud', 'pm-cloud', 'ad-cloud'): return get_setting('check.%s' % scraper) == "true"
	if get_setting('check.%s' % scraper) == "true" and get_setting('auto_play') != "true": return True
	else: return False

def skip_duplicates():
	return get_setting('skip_duplicates') == "true"

def internal_scraper_order():
	setting = get_setting('results.internal_scrapers_order')
	if setting in ('', None):
		setting = 'FILES, FURK, EASYNEWS, CLOUD'
	return setting.split(', ')

def internal_scrapers_order_display():
	setting = get_setting('results.internal_scrapers_order_display')
	if setting in ('', None):
		setting = '$ADDON[plugin.video.fen 32493], $ADDON[plugin.video.fen 32069], $ADDON[plugin.video.fen 32070], $ADDON[plugin.video.fen 32586]'
	return setting.split(', ')

def results_sort_order():
	results_sort_order = get_setting('results.sort_order')
	if results_sort_order == '0': return ['quality_rank', 'internal_rank', 'host_rank', 'name_rank', 'external_size', 'size', 'debrid_rank'] #Quality, Provider, Size, Debrid
	if results_sort_order == '1': return ['quality_rank', 'internal_rank', 'host_rank', 'external_size', 'size', 'name_rank', 'debrid_rank'] #Quality, Size, Provider, Debrid
	if results_sort_order == '2': return ['internal_rank', 'host_rank', 'name_rank', 'quality_rank', 'external_size', 'size', 'debrid_rank'] #Provider, Quality, Size, Debrid
	if results_sort_order == '3': return ['internal_rank', 'host_rank', 'name_rank', 'external_size', 'size', 'quality_rank', 'debrid_rank'] #Provider, Size, Quality, Debrid
	if results_sort_order == '4': return ['external_size', 'size', 'quality_rank', 'internal_rank', 'host_rank', 'name_rank', 'debrid_rank'] #Size, Quality, Provider, Debrid
	if results_sort_order == '5': return ['external_size', 'size', 'internal_rank', 'host_rank', 'name_rank', 'quality_rank', 'debrid_rank'] #Size, Provider, Quality, Debrid
	return ['quality_rank', 'internal_rank', 'host_rank', 'name_rank', 'external_size', 'size', 'debrid_rank'] #Quality, Provider, Size, Debrid

def sorted_first(scraper_setting):
	return get_setting('results.%s' % scraper_setting) == "true"

def provider_color(provider):
	return get_setting('provider.%s_colour' % provider)

def active_scrapers(group_folders=False):
	folders = ['folder1', 'folder2', 'folder3', 'folder4', 'folder5']
	settings = ['provider.external', 'provider.furk', 'provider.easynews', 'provider.rd-cloud', 'provider.pm-cloud', 'provider.ad-cloud']
	active = [i.split('.')[1] for i in settings if get_setting(i) == 'true']
	if get_setting('provider.folders') == 'true':
		if group_folders: active.append('folders')
		else: active += folders
	return active

def auto_resume():
	auto_resume = get_setting('auto_resume')
	if auto_resume == '1': return True
	if auto_resume == '2' and auto_play(): return True
	else: return False

def set_resume():
	return float(get_setting('resume.threshold'))

def set_watched():
	return float(get_setting('watched.threshold'))

def nextep_threshold():
	return float(get_setting('nextep.threshold'))

def nav_jump_use_alphabet():
	if get_setting('cache_browsed_page') == 'true': return False
	if get_setting('nav_jump') == '0': return False
	else: return True

def use_season_title():
	return get_setting('use_season_title') == "true"

def unaired_episode_colour():
	return get_setting('unaired_episode_colour', 'red')

def nextep_airdate_format():
	date_format = get_setting('nextep.airdate_format')
	if date_format == '0': return '%d-%m-%Y'
	elif date_format == '1': return '%Y-%m-%d'
	elif date_format == '2': return '%m-%d-%Y'
	else: return '%Y-%m-%d'

def nextep_display_settings():
	include_airdate = get_setting('nextep.include_airdate') == 'true'
	airdate_colour = get_setting('nextep.airdate_colour', 'magenta')
	unaired_colour = get_setting('nextep.unaired_colour', 'red')
	unwatched_colour = get_setting('nextep.unwatched_colour', 'darkgoldenrod')
	return {'include_airdate': include_airdate, 'airdate_colour': airdate_colour,
			'unaired_colour': unaired_colour, 'unwatched_colour': unwatched_colour}

def nextep_content_settings():
	sort_type = int(get_setting('nextep.sort_type'))
	sort_order = int(get_setting('nextep.sort_order'))
	sort_direction = True if sort_order == 0 else False
	sort_key = 'curr_last_played_parsed' if sort_type == 0 else 'first_aired' if sort_type == 1 else 'name'
	cache_to_disk = get_setting('nextep.cache_to_disk') == 'true'
	include_unaired = get_setting('nextep.include_unaired') == 'true'
	include_unwatched = get_setting('nextep.include_unwatched') == 'true'
	include_in_progress = get_setting('nextep.include_in_progress', 'false') == 'true'
	return {'cache_to_disk': cache_to_disk, 'sort_key': sort_key, 'sort_direction': sort_direction, 'sort_type': sort_type, 'sort_order':sort_order,
			'include_unaired': include_unaired, 'include_unwatched': include_unwatched, 'include_in_progress': include_in_progress}

def scraping_settings():
	multiline_highlight = get_setting('secondline.identify', 'white')
	hoster_highlight = get_setting('hoster.identify', 'dodgerblue')
	torrent_highlight = get_setting('torrent.identify', 'magenta')
	furk_highlight = provider_color('furk')
	easynews_highlight = provider_color('easynews')
	rdcloud_highlight = provider_color('rd-cloud')
	pmcloud_highlight = provider_color('pm-cloud')
	adcloud_highlight = provider_color('ad-cloud')
	folders_highlight = provider_color('folders')
	return {'hoster_highlight': hoster_highlight, 'torrent_highlight': torrent_highlight, 'furk_highlight': furk_highlight, 'easynews_highlight': easynews_highlight,
			'rd-cloud_highlight': rdcloud_highlight, 'pm-cloud_highlight': pmcloud_highlight, 'ad-cloud_highlight': adcloud_highlight, 'folders_highlight': folders_highlight}

def tvdbJWToken():
	return get_setting('tvdb.jwtoken')

def get_fanart_data():
	return get_setting('get_fanart_data') == 'true'

def get_resolution():
	resolution = get_setting('image_resolutions', '2')
	if resolution == '0': return {'poster': 'w185', 'fanart': 'w300', 'still': 'w92', 'profile': 'w185'}
	if resolution == '1': return {'poster': 'w342', 'fanart': 'w780', 'still': 'w185', 'profile': 'w185'}
	if resolution == '2': return {'poster': 'w780', 'fanart': 'w1280', 'still': 'w300', 'profile': 'h632'}
	if resolution == '3': return {'poster': 'original', 'fanart': 'original', 'still': 'original', 'profile': 'original'}
	else: return {'poster': 'w780', 'fanart': 'w1280', 'still': 'w185', 'profile': 'w185'}

def get_language():
	return get_setting('meta_language', 'en')

def user_info():
	tvdb_jwtoken = tvdbJWToken()
	extra_fanart_enabled = get_fanart_data()
	image_resolution = get_resolution()
	meta_language = get_language()
	return {'tvdb_jwtoken': tvdb_jwtoken, 'extra_fanart_enabled': extra_fanart_enabled, 'image_resolution': image_resolution , 'language': meta_language}

def list_actions_global():
	global list_actions
	list_actions = []

def initialize_databases():
	import xbmcvfs
	import os
	try: from sqlite3 import dbapi2 as database
	except ImportError: from pysqlite2 import dbapi2 as database
	from modules.settings_reader import make_settings_dict
	DATA_PATH = xbmc.translatePath('special://profile/addon_data/plugin.video.fen/')
	if not xbmcvfs.exists(DATA_PATH): xbmcvfs.mkdirs(DATA_PATH)
	NAVIGATOR_DB = os.path.join(DATA_PATH, "navigator.db")
	WATCHED_DB = os.path.join(DATA_PATH, "watched_status.db")
	FAVOURITES_DB = os.path.join(DATA_PATH, "favourites.db")
	VIEWS_DB = os.path.join(DATA_PATH, "views.db")
	TRAKT_DB = os.path.join(DATA_PATH, "fen_trakt2.db")
	FEN_DB = os.path.join(DATA_PATH, "fen_cache2.db")
	make_settings_dict()
	#Always check NAVIGATOR.
	dbcon = database.connect(NAVIGATOR_DB)
	dbcon.execute("""CREATE TABLE IF NOT EXISTS navigator
					  (list_name text, list_type text, list_contents text) 
				   """)
	if not xbmcvfs.exists(WATCHED_DB):
		dbcon = database.connect(WATCHED_DB)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS progress
						  (db_type text, media_id text, season integer, episode integer,
						  resume_point text, curr_time text,
						  unique(db_type, media_id, season, episode)) 
					   """)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS watched_status
						  (db_type text, media_id text, season integer,
						  episode integer, last_played text, title text,
						  unique(db_type, media_id, season, episode)) 
					   """)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS exclude_from_next_episode
						  (media_id text, title text) 
					   """)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS unwatched_next_episode
						  (media_id text) 
					   """)
		dbcon.close()
	if not xbmcvfs.exists(FAVOURITES_DB):
		dbcon = database.connect(FAVOURITES_DB)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS favourites
						  (db_type text, tmdb_id text, title text, unique (db_type, tmdb_id)) 
					   """)
		dbcon.close()
	if not xbmcvfs.exists(VIEWS_DB):
		dbcon = database.connect(VIEWS_DB)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS views
						  (view_type text, view_id text, unique (view_type)) 
					   """)
		dbcon.close()
	if not xbmcvfs.exists(TRAKT_DB):
		dbcon = database.connect(TRAKT_DB)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS fentrakt(
					id text unique, data text, expires INTEGER)
							""")
		dbcon.close()
	if not xbmcvfs.exists(FEN_DB):
		dbcon = database.connect(FEN_DB)
		dbcon.execute("""CREATE TABLE IF NOT EXISTS fencache(
					id text unique, data text, expires INTEGER)
							""")
		dbcon.close()
	return True
