# -*- coding: utf-8 -*-

import xbmc
from metadata import tmdb
from metadata import tvdb
from metadata import trakt
from metadata import fanarttv
from metadata.tmdb import tmdbMoviesExternalID, tmdbTVShowsExternalID
from caches.metacache import metacache
from modules.utils import try_parse_int, safe_string, remove_accents, to_utf8
# from modules.utils import logger

backup_resolutions = {'poster': 'w780', 'fanart': 'w1280', 'still': 'w185', 'profile': 'w185'}

def movie_meta(id_type, media_id, user_info, hours=720):
	from datetime import timedelta
	meta = None
	image_resolution = user_info.get('image_resolution', backup_resolutions)
	language = user_info['language']
	extra_fanart_enabled = user_info['extra_fanart_enabled']
	def tmdb_meta(language):
		data = tmdb.tmdbMovies
		result = tmdb.tmdbMoviesExternalID
		return data(media_id, language) if id_type == 'tmdb_id' else data(result(id_type, media_id)['id'], language)
	def tmdb_meta_search():
		data = tmdb.tmdbMoviesTitleYear()
		media_id = data['id']
		id_type = 'tmdb_id'
		return tmdb_meta(language)
	def fanarttv_meta(fanart_id):
		if extra_fanart_enabled: return fanarttv.get('movies', language, fanart_id)
		else: return None
	def cached_meta():
		return metacache.get('movie', id_type, media_id)
	def set_cache_meta():
		metacache.set('movie', meta, timedelta(hours=hours))
	def delete_cache_meta():
		metacache.delete('movie', 'tmdb_id', meta['tmdb_id'])
	def check_tmdb_data(tmdb_data):
		if language != 'en' and tmdb_data['overview'] == '':
			overview = tmdb_meta('en')['overview']
			tmdb_data['overview'] = overview
		return tmdb_data
	meta = cached_meta()
	if meta and extra_fanart_enabled and not meta.get('fanart_added', False):
		try:
			meta = fanarttv.add('movies', language, meta['tmdb_id'], meta)
			delete_cache_meta()
			set_cache_meta()
		except: pass
	if not meta:
		try:
			fetch_fanart_art = False
			tmdb_data = check_tmdb_data(tmdb_meta(language))
			if not tmdb_data.get('poster_path', None):
				if extra_fanart_enabled: fetch_fanart_art = True
			fanarttv_data = fanarttv_meta(tmdb_data['id'])
			if fetch_fanart_art:
				tmdb_data['external_poster'] = fanarttv_data.get('fanarttv_poster', None)
				tmdb_data['external_fanart'] = fanarttv_data.get('fanarttv_fanart', None)
			tmdb_data['image_resolution'] = image_resolution
			meta = build_movie_meta(tmdb_data, fanarttv_data=fanarttv_data)
			set_cache_meta()
		except: pass
	return meta

def tvshow_meta(id_type, media_id, user_info, hours=96):
	from datetime import timedelta
	meta = None
	tvdb_jwtoken = user_info['tvdb_jwtoken']
	image_resolution = user_info.get('image_resolution', backup_resolutions)
	language = user_info['language']
	extra_fanart_enabled = user_info['extra_fanart_enabled']
	def tmdb_meta():
		data = tmdb.tmdbTVShows
		result = tmdb.tmdbTVShowsExternalID
		return data(media_id, language) if id_type == 'tmdb_id' else data(result(id_type, media_id)['id'], language)
	def tvdb_meta(tvdb_id):
		tvdb_summary = tvdb.TvdbAPI(tvdb_jwtoken).get_series_episodes_summary(tvdb_id)
		return tvdb_summary
	def trakt_ids(id_type, _id):
		all_trakt_ids = trakt.traktGetIDs('show', id_type, str(_id))
		return all_trakt_ids
	def tvdb_overview(tvdb_id):
		tvdb_overview = tvdb.TvdbAPI(tvdb_jwtoken).get_series_overview(tvdb_id, language)
		return tvdb_overview
	def fanarttv_meta(fanart_id):
		if extra_fanart_enabled: return fanarttv.get('tv', language, fanart_id)
		else: return None
	def cached_meta():
		return metacache.get('tvshow', id_type, media_id)
	def set_cache_meta():
		metacache.set('tvshow', meta, timedelta(hours=hours))
	def delete_cache_meta():
		metacache.delete('tvshow', 'tmdb_id', meta['tmdb_id'])
	def check_tmdb_data(tvdb_id, tmdb_data):
		if language != 'en' and tmdb_data['overview'] == '':
			overview = tvdb_overview(tvdb_id)
			tmdb_data['overview'] = overview
		return tmdb_data
	meta = cached_meta()
	if meta and extra_fanart_enabled and not meta.get('fanart_added', False):
		try:
			meta = fanarttv.add('tv', language, meta['tvdb_id'], meta)
			delete_cache_meta()
			set_cache_meta()
		except: pass
	if meta and not 'tvdb_summary' in meta:
		delete_cache_meta()
		meta = None
	if not meta:
		try:
			tvdb_summary = None
			tvdb_data = None
			fanarttv_data = None
			tmdb_data = tmdb_meta()
			tmdb_data['image_resolution'] = image_resolution
			tvdb_id = tmdb_data['external_ids']['tvdb_id']
			if not tvdb_id:
				imdb_id = tmdb_data['external_ids']['imdb_id']
				if imdb_id:
					tvdb_data = tvdb.TvdbAPI(tvdb_jwtoken).get_series_by_imdb_id(imdb_id)
					if tvdb_data: tvdb_id = tvdb_data.get('id', None)
				if not tvdb_id:
					tvdb_data = tvdb.TvdbAPI(tvdb_jwtoken).get_series_by_name(tmdb_data['name'])
					if tvdb_data: tvdb_id = tvdb_data.get('id', None)
				if tvdb_data:
					tmdb_data['external_ids']['tvdb_id'] = tvdb_id
					if not tmdb_data['poster_path']:
						if tvdb_data.get('poster', None):
							if 'banners' in tvdb_data['poster']: tmdb_data['external_poster'] = "http://thetvdb.com%s" % tvdb_data['poster']
							else: tmdb_data['external_poster'] = "http://thetvdb.com/banners/%s" % tvdb_data['poster']
						elif tvdb_data.get('image', None):
							if 'banners' in tvdb_data['image']: tmdb_data['external_poster'] = "http://thetvdb.com%s" % tvdb_data['image']
							else: tmdb_data['external_poster'] = "http://thetvdb.com/banners/%s" % tvdb_data['image']
					if not tmdb_data['backdrop_path']:
						if tvdb_data.get('fanart', None):
							if 'banners' in tvdb_data['poster']: tmdb_data['external_fanart'] = "http://thetvdb.com%s" % tvdb_data['fanart']
							else: tmdb_data['external_fanart'] = "http://thetvdb.com/banners/%s" % tvdb_data['fanart']
			if tvdb_id:
				tvdb_data = None
				tmdb_data = check_tmdb_data(tvdb_id, tmdb_data)
				tvdb_summary = tvdb_meta(tvdb_id)
				if not tmdb_data['poster_path'] and not tmdb_data.get('external_poster', None):
					tvdb_data = tvdb.TvdbAPI(tvdb_jwtoken).get_series(tvdb_id, language)
					if tvdb_data.get('poster', None):
						if 'banners' in tvdb_data['poster']: tmdb_data['external_poster'] = "http://thetvdb.com%s" % tvdb_data['poster']
						else: tmdb_data['external_poster'] = "http://thetvdb.com/banners/%s" % tvdb_data['poster']
					elif tvdb_data.get('image', None):
						if 'banners' in tvdb_data['image']: tmdb_data['external_poster'] = "http://thetvdb.com%s" % tvdb_data['image']
						else: tmdb_data['external_poster'] = "http://thetvdb.com/banners/%s" % tvdb_data['image']
				if not tmdb_data['backdrop_path'] and not tmdb_data.get('external_fanart', None):
					if not tvdb_data: tvdb_data = tvdb.TvdbAPI(tvdb_jwtoken).get_series(tvdb_id, language)
					if tvdb_data.get('fanart', None):
						if 'banners' in tvdb_data['poster']: tmdb_data['external_fanart'] = "http://thetvdb.com%s" % tvdb_data['fanart']
						else: tmdb_data['external_fanart'] = "http://thetvdb.com/banners/%s" % tvdb_data['fanart']
				if tvdb_summary['airedSeasons'] == []:
					tvdb_summary = None
			fanarttv_data = fanarttv_meta(tvdb_id)
			meta = build_tvshow_meta(tmdb_data, fanarttv_data=fanarttv_data, tvdb_summary=tvdb_summary)
			set_cache_meta()
		except: pass
	return meta

def all_episodes_meta(media_id, tvdb_id, seasons, tmdb_data, user_info, hours=96):
	def _reset_meta(tvdb_id):
		series_meta['tvdb_id'] = tvdb_id
		metacache.delete('tvshow', 'tmdb_id', media_id)
		metacache.set('tvshow', series_meta, timedelta(hours=hours), media_id)
		data = tvdb.TvdbAPI(user_info['tvdb_jwtoken']).get_all_episodes(tvdb_id, language)
		return _return_meta(data)
	def _get_tmdb_episodes(season):
		try:
			episodes = tmdb.tmdbSeasonEpisodes(media_id, season, language)['episodes']
			tmdb_data = {'season': season, 'episode_info': episodes}
			all_tmdb_episodes.append(tmdb_data)
		except: pass
	def _return_meta(data, use_tmdb=False):
		meta = build_seasons_meta(data, seasons, tmdb_data, image_resolution, use_tmdb=use_tmdb)
		metacache.set('season', meta, timedelta(hours=hours), media_id)
		return meta
	image_resolution = user_info.get('image_resolution', backup_resolutions)
	language = user_info['language']
	meta = None
	use_tmdb = False
	all_tmdb_episodes = []
	threads = []
	data = metacache.get('season', 'tmdb_id', media_id)
	if data: return data
	try:
		from datetime import timedelta
		if tvdb_id: data = tvdb.TvdbAPI(user_info['tvdb_jwtoken']).get_all_episodes(tvdb_id, language)
		if data: return _return_meta(data)
		from threading import Thread
		series_meta = tvshow_meta('tmdb_id', media_id, user_info)
		imdb_id = series_meta['imdb_id']
		if imdb_id: data = tvdb.TvdbAPI(user_info['tvdb_jwtoken']).get_series_by_imdb_id(imdb_id)
		if data: _reset_meta(data['id'])
		for i in seasons: threads.append(Thread(target=_get_tmdb_episodes, args=(int(i),)))
		[i.start() for i in threads]
		[i.join() for i in threads]
		data = all_tmdb_episodes
		use_tmdb = True
	except: pass
	return _return_meta(data, use_tmdb)

def season_episodes_meta(media_id, tvdb_id, season, seasons, tmdb_data, user_info, all_episodes=False, hours=96):
	data = None
	episodes_data = None
	image_resolution = user_info.get('image_resolution', backup_resolutions)
	data = metacache.get('season', 'tmdb_id', media_id)
	if not data: data = all_episodes_meta(media_id, tvdb_id, seasons, tmdb_data, user_info)
	if data:
		use_tmdb = data[0].get('use_tmdb', False)
		if use_tmdb:
			episodes_data = tmdb.tmdbSeasonEpisodes(media_id, season, user_info['language'])['episodes']
		else:
			if all_episodes:
				episodes_data = []
				data = [i['episodes_data'] for i in data]
				for item in data:
					for ep in item:
						episodes_data.append(ep)
			else:
				episodes_data = [i['episodes_data'] for i in data if i['season_number'] == int(season)][0]
		episodes_data = build_episodes_meta(episodes_data, image_resolution, use_tmdb=use_tmdb)
	return episodes_data

def build_movie_meta(data, fanarttv_data=None):
	meta = {}
	writer = []
	meta['cast'] = []
	meta['studio'] = []
	meta['all_trailers'] = []
	meta['extra_info'] = {}
	meta['mpaa'] = ''
	meta['director'] = ''
	meta['premiered'] = ''
	meta['writer'] = ''
	meta['trailer'] = ''
	meta['tmdb_id'] = data['id'] if 'id' in data else ''
	meta['imdb_id'] = data.get('imdb_id', '')
	meta['imdbnumber'] = meta['imdb_id']
	meta['tvdb_id'] = 'None'
	if data.get('poster_path'):
		meta['poster'] = "https://image.tmdb.org/t/p/%s%s" % (data['image_resolution']['poster'], data.get('poster_path'))
	elif data.get('external_poster'):
		meta['poster'] = data['external_poster']
	else:
		meta['poster'] = xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/default_images/meta_blank_poster.png')
	if data.get('backdrop_path'):
		meta['fanart'] = "https://image.tmdb.org/t/p/%s%s" % (data['image_resolution']['fanart'], data.get('backdrop_path'))
	elif data.get('external_fanart'):
		meta['fanart'] = data['external_fanart']
	else:
		meta['fanart'] = xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/default_images/meta_blank_fanart.png')
	if fanarttv_data:
		meta['banner'] = fanarttv_data['banner']
		meta['clearart'] = fanarttv_data['clearart']
		meta['clearlogo'] = fanarttv_data['clearlogo']
		meta['landscape'] = fanarttv_data['landscape']
		meta['discart'] = fanarttv_data['discart']
		meta['fanart_added'] = True
	else:
		meta['banner'] = xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/default_images/meta_blank_banner.png')
		meta['clearart'] = ''
		meta['clearlogo'] = ''
		meta['landscape'] = ''
		meta['discart'] = ''
		meta['fanart_added'] = False
	meta['rating'] = data['vote_average'] if 'vote_average' in data else ''
	try: meta['genre'] = ', '.join([item['name'] for item in data['genres']])
	except: meta['genre'] == []
	meta['plot'] = to_utf8(data['overview']) if 'overview' in data else ''
	meta['tagline'] = to_utf8(data['tagline']) if 'tagline' in data else ''
	meta['votes'] = data['vote_count'] if 'vote_count' in data else ''
	meta['mediatype'] = 'movie'
	meta['title'] = to_utf8(data['title'])
	try: meta['search_title'] = to_utf8(safe_string(remove_accents(data['title'])))
	except: meta['search_title'] = to_utf8(safe_string(data['title']))
	try: meta['original_title'] = to_utf8(safe_string(remove_accents(data['original_title'])))
	except: meta['original_title'] = to_utf8(safe_string(data['original_title']))
	try: meta['year'] = try_parse_int(data['release_date'].split('-')[0])
	except: meta['year'] = ''
	meta['duration'] = int(data['runtime'] * 60) if data.get('runtime') else 90 * 60
	if data.get('production_companies'): meta['studio'] = [item['name'] for item in data['production_companies']][0]
	if data.get('release_date'): meta['premiered'] = data['release_date']
	meta['rootname'] = '{0} ({1})'.format(meta['search_title'], meta['year'])
	if 'content_ratings' in data:
		for rat_info in data['content_ratings']['results']:
			if rat_info['iso_3166_1'] == 'US':
				meta['mpaa'] = rat_info['rating']
	if 'release_dates' in data:
		for rel_info in data['release_dates']['results']:
			if rel_info['iso_3166_1'] == 'US':
				meta['mpaa'] = rel_info['release_dates'][0]['certification']
	if 'credits' in data:
		if 'cast' in data['credits']:
			for cast_member in data['credits']['cast']:
				cast_thumb = ''
				if cast_member['profile_path']:
					cast_thumb = 'https://image.tmdb.org/t/p/%s%s' % (data['image_resolution']['profile'], cast_member['profile_path'])
				meta['cast'].append({'name': cast_member['name'], 'role': cast_member['character'], 'thumbnail': cast_thumb})
		if 'crew' in data['credits']:
			for crew_member in data['credits']['crew']:
				cast_thumb = ''
				if crew_member['profile_path']:
					cast_thumb = 'https://image.tmdb.org/t/p/%s%s' % (data['image_resolution']['profile'], crew_member['profile_path'])
				if crew_member['job'] in ['Author', 'Writer', 'Screenplay', 'Characters']:
					writer.append(crew_member['name'])
				if crew_member['job'] == 'Director':
					meta['director'] = crew_member['name']
			if writer: meta['writer'] = ', '.join(writer)
	if 'alternative_titles' in data:
		alternatives = data['alternative_titles']['titles']
		meta['alternative_titles'] = [i['title'] for i in alternatives if i['iso_3166_1'] == 'US']
	if 'videos' in data:
		meta['all_trailers'] = data['videos']['results']
		for video in data['videos']['results']:
			if video['site'] == 'YouTube' and video['type'] == 'Trailer' or video['type'] == 'Teaser':
				meta['trailer'] = 'plugin://plugin.video.youtube/play/?video_id=%s' % video['key']
				break
	if data.get('belongs_to_collection', False):
		meta['extra_info']['collection_name'] = data['belongs_to_collection']['name']
		meta['extra_info']['collection_id'] = data['belongs_to_collection']['id']
	else:
		meta['extra_info']['collection_name'] = None
		meta['extra_info']['collection_id'] = None
	meta['extra_info']['budget'] = '${:,}'.format(data['budget'])
	meta['extra_info']['revenue'] = '${:,}'.format(data['revenue'])
	meta['extra_info']['homepage'] = data.get('homepage', 'N/A')
	meta['extra_info']['status'] = data.get('status', 'N/A')
	return meta

def build_tvshow_meta(data, fanarttv_data=None, tvdb_summary=None):
	meta = {}
	writer = []
	creator = []
	meta['cast'] = []
	meta['studio'] = []
	meta['all_trailers'] = []
	meta['extra_info'] = {}
	meta['mpaa'] = ''
	meta['director'] = ''
	meta['premiered'] = ''
	meta['writer'] = ''
	meta['trailer'] = ''
	meta['tmdb_id'] = data['id'] if 'id' in data else ''
	meta['imdb_id'] = data['external_ids'].get('imdb_id', '')
	meta['imdbnumber'] = meta['imdb_id']
	meta['tvdb_id'] = data['external_ids'].get('tvdb_id', 'None')
	if data.get('poster_path'):
		meta['poster'] = "https://image.tmdb.org/t/p/%s%s" % (data['image_resolution']['poster'], data.get('poster_path'))
	elif data.get('external_poster'):
		meta['poster'] = data['external_poster']
	else:
		meta['poster'] = xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/default_images/meta_blank_poster.png')
	if data.get('backdrop_path'):
		meta['fanart'] = "https://image.tmdb.org/t/p/%s%s" % (data['image_resolution']['fanart'], data.get('backdrop_path'))
	elif data.get('external_fanart'):
		meta['fanart'] = data['external_fanart']
	else:
		meta['fanart'] = xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/default_images/meta_blank_fanart.png')
	if fanarttv_data:
		meta['banner'] = fanarttv_data['banner']
		meta['clearart'] = fanarttv_data['clearart']
		meta['clearlogo'] = fanarttv_data['clearlogo']
		meta['landscape'] = fanarttv_data['landscape']
		meta['discart'] = fanarttv_data['discart']
		meta['fanart_added'] = True
	else:
		meta['banner'] = xbmc.translatePath('special://home/addons/script.tiki.artwork/resources/default_images/meta_blank_banner.png')
		meta['clearart'] = ''
		meta['clearlogo'] = ''
		meta['landscape'] = ''
		meta['discart'] = ''
		meta['fanart_added'] = False
	meta['rating'] = data['vote_average'] if 'vote_average' in data else ''
	try: meta['genre'] = ', '.join([item['name'] for item in data['genres']])
	except: meta['genre'] == []
	meta['plot'] = to_utf8(data['overview']) if 'overview' in data else ''
	meta['tagline'] = to_utf8(data['tagline']) if 'tagline' in data else ''
	meta['votes'] = data['vote_count'] if 'vote_count' in data else ''
	meta['mediatype'] = 'tvshow'
	meta['title'] = to_utf8(data['name'])
	try: meta['search_title'] = to_utf8(safe_string(remove_accents(data['name'])))
	except: meta['search_title'] = to_utf8(safe_string(data['name']))
	try: meta['original_title'] = to_utf8(safe_string(remove_accents(data['original_name'])))
	except: meta['original_title'] = to_utf8(safe_string(data['original_name']))
	meta['tvshowtitle'] = meta['title']
	try: meta['year'] = try_parse_int(data['first_air_date'].split('-')[0])
	except: meta['year'] = ''
	meta['premiered'] = data['first_air_date']
	meta['season_data'] = data['seasons']
	if tvdb_summary:
		meta['tvdb_summary'] = tvdb_summary
		meta['total_episodes'] = int(data['number_of_episodes'])
		meta['total_seasons'] = len([i for i in tvdb_summary['airedSeasons'] if not i == '0'])
	else:
		meta['tvdb_summary'] = {'airedEpisodes': data['number_of_episodes'], 'airedSeasons': [str(i['season_number']) for i in data['seasons']]}
		meta['total_episodes'] = data['number_of_episodes']
		meta['total_seasons'] = data['number_of_seasons']
	try: meta['duration'] = min(data['episode_run_time']) * 60
	except: meta['duration'] = 30 * 60
	if data.get('networks', None):
		try: meta['studio'] = [item['name'] for item in data['networks']][0]
		except: meta['studio'] = ''
	meta['rootname'] = '{0} ({1})'.format(meta['search_title'], meta['year'])
	if 'content_ratings' in data:
		for rat_info in data['content_ratings']['results']:
			if rat_info['iso_3166_1'] == 'US':
				meta['mpaa'] = rat_info['rating']
	if 'release_dates' in data:
		for rel_info in data['release_dates']['results']:
			if rel_info['iso_3166_1'] == 'US':
				meta['mpaa'] = rel_info['release_dates'][0]['certification']
	if 'credits' in data:
		if 'cast' in data['credits']:
			for cast_member in data['credits']['cast']:
				cast_thumb = ''
				if cast_member['profile_path']:
					cast_thumb = 'https://image.tmdb.org/t/p/%s%s' % (data['image_resolution']['profile'], cast_member['profile_path'])
				meta['cast'].append({'name': cast_member['name'], 'role': cast_member['character'], 'thumbnail': cast_thumb})
		if 'crew' in data['credits']:
			for crew_member in data['credits']['crew']:
				cast_thumb = ''
				if crew_member['profile_path']:
					cast_thumb = 'https://image.tmdb.org/t/p/%s%s' % (data['image_resolution']['profile'], crew_member['profile_path'])
				if crew_member['job'] in ['Author', 'Writer', 'Screenplay', 'Characters']:
					writer.append(crew_member['name'])
				if crew_member['job'] == 'Director':
					meta['director'] = crew_member['name']
			if writer: meta['writer'] = ', '.join(writer)
	if 'alternative_titles' in data:
		alternatives = data['alternative_titles']['results']
		meta['alternative_titles'] = [i['title'] for i in alternatives if i['iso_3166_1'] == 'US']
	if 'videos' in data:
		meta['all_trailers'] = data['videos']['results']
		for video in data['videos']['results']:
			if video['site'] == 'YouTube' and video['type'] == 'Trailer' or video['type'] == 'Teaser':
				meta['trailer'] = 'plugin://plugin.video.youtube/play/?video_id=%s' % video['key']
				break
	if data.get('created_by', False):
		for person in data['created_by']:
			creator.append(person['name'])
		if creator: meta['extra_info']['created_by'] = ', '.join(creator)
	else: meta['extra_info']['created_by'] = 'N/A'
	if data.get('next_episode_to_air', False):
		next_ep = data['next_episode_to_air']
		meta['extra_info']['next_episode_to_air'] = '[%s] S%.2dE%.2d - %s' % \
					(next_ep['air_date'], next_ep['season_number'], next_ep['episode_number'], next_ep['name'])
	else: meta['extra_info']['next_episode_to_air'] = 'N/A'
	if data.get('last_episode_to_air', False):
		last_ep = data['last_episode_to_air']
		meta['extra_info']['last_episode_to_air'] = '[%s] S%.2dE%.2d - %s' % \
					(last_ep['air_date'], last_ep['season_number'], last_ep['episode_number'], last_ep['name'])
	else: meta['extra_info']['last_episode_to_air'] = 'N/A'
	meta['extra_info']['type'] = data.get('type', 'N/A')
	meta['extra_info']['status'] = data.get('status', 'N/A')
	meta['extra_info']['homepage'] = data.get('homepage', 'N/A')
	return meta

def build_seasons_meta(data, seasons, tmdb_data, image_resolution, use_tmdb=False):
	seasons = sorted([int(i) for i in seasons])
	meta = []
	for i in seasons:
		season_info = {}
		season_info['poster_path'] = None
		season_info['overview'] = ''
		season_info['name'] = ''
		season_info['season_number'] = i
		if use_tmdb:
			tmdb_info = [d['episode_info'] for d in data if d['season'] == i][0]
			season_info['use_tmdb'] = True
			season_info['episodes_data'] = tmdb_info
			season_info['episode_count'] = len(tmdb_info)
		else:
			episodes = [d for d in data if d['airedSeason'] == i]
			season_info['episodes_data'] = episodes
			season_info['episode_count'] = len(episodes)
		try: season_info['poster_path'] = ["https://image.tmdb.org/t/p/%s%s" % (image_resolution['poster'], p['poster_path']) for p in tmdb_data if p['season_number'] == i and p['poster_path'] is not None][0]
		except: pass
		try: season_info['overview'] = [p['overview'] for p in tmdb_data if p['season_number'] == i][0]
		except: pass
		try: season_info['name'] = [p['name'] for p in tmdb_data if p['season_number'] == i][0]
		except: pass
		meta.append(season_info)
	return meta

def build_episodes_meta(data, image_resolution, use_tmdb=False):
	meta = []
	if use_tmdb:
		for i in data:
			episode_info = {}
			writer = []
			episode_info['writer'] = ''
			episode_info['director'] = ''
			if 'crew' in data:
				for crew_member in data['crew']:
					if crew_member['job'] in ['Author', 'Writer', 'Screenplay', 'Characters']:
						writer.append(crew_member['name'])
					if crew_member['job'] == 'Director':
						episode_info['director'] = crew_member['name']
				if writer: episode_info['writer'] = ', '.join(writer)
			episode_info['mediatype'] = 'episode'
			episode_info['title'] = i['name']
			episode_info['plot'] = i['overview']
			episode_info['premiered'] = i['air_date']
			episode_info['season'] = i['season_number']
			episode_info['episode'] = i['episode_number']
			if i.get('still_path', None) is not None:
				episode_info['thumb'] = 'https://image.tmdb.org/t/p/%s%s' % (image_resolution['still'], i['still_path'])
			else: episode_info['thumb'] = None
			episode_info['rating'] = i['vote_average']
			episode_info['votes'] = i['vote_count']
			meta.append(episode_info)
	else:
		for i in data:
			episode_info = {}
			episode_info['writer'] = ''
			episode_info['director'] = ''
			episode_info['mediatype'] = 'episode'
			episode_info['title'] = i['episodeName']
			episode_info['plot'] = i['overview']
			episode_info['premiered'] = i['firstAired']
			episode_info['season'] = i['airedSeason']
			episode_info['episode'] = i['airedEpisodeNumber']
			episode_info['thumb'] = 'https://www.thetvdb.com/banners/%s' % i['filename'] if 'episodes' in i['filename'] else None
			episode_info['rating'] = i['siteRating']
			episode_info['votes'] = i['siteRatingCount']
			episode_info['writer'] = ', '.join(i['writers'])
			episode_info['director'] = ', '.join(i['directors'])
			meta.append(episode_info)
	return meta

def movie_meta_external_id(external_source, external_id):
	return tmdbMoviesExternalID(external_source, external_id)

def tvshow_meta_external_id(external_source, external_id):
	return tmdbTVShowsExternalID(external_source, external_id)

def delete_cache_item(db_type, id_type, media_id):
	return metacache.delete(db_type, id_type, media_id)

def retrieve_user_info():
	import xbmcgui
	from modules.settings import user_info
	xbmcgui.Window(10000).setProperty('fen_fanart_error', 'true')
	return user_info()

def check_meta_database():
	metacache.check_database()

def delete_meta_cache(silent=False):
	from modules.utils import local_string as ls
	try:
		if not silent:
			import xbmcgui
			if not xbmcgui.Dialog().yesno('Fen', ls(32580)): return False
		metacache.delete_all()
		return True
	except:
		return False
