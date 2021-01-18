# -*- coding: utf-8 -*-

import xbmc
from tikimeta.setting_reader import get_setting, set_setting

def logger(heading, function):
	xbmc.log('###%s###: %s' % (heading, function), 2)

def notification(line1, time=5000, icon=None, sound=False):
	import xbmcgui
	if not icon:
		import os
		icon = os.path.join(xbmc.translatePath('special://home/addons/script.module.tikimeta'), "icon.png")
	xbmcgui.Dialog().notification('Tiki Meta', line1, icon, time, sound)

def get_kodi_version():
	return int(xbmc.getInfoLabel("System.BuildVersion")[0:2])

def safe_string(obj):
	try:
		try:
			return str(obj)
		except UnicodeEncodeError:
			return obj.encode('utf-8', 'ignore').decode('ascii', 'ignore')
		except:
			return ""
	except: return obj

def remove_accents(obj):
	import unicodedata
	try:
		try: obj = u'%s' % obj
		except: pass
		obj = ''.join(c for c in unicodedata.normalize('NFD', obj) if unicodedata.category(c) != 'Mn')
	except: pass
	return obj

def to_utf8(obj):
	try:
		import copy
		if isinstance(obj, unicode):
			obj = obj.encode('utf-8', 'ignore')
		elif isinstance(obj, dict):
			obj = copy.deepcopy(obj)
			for key, val in obj.items():
				obj[key] = to_utf8(val)
		elif obj is not None and hasattr(obj, "__iter__"):
			obj = obj.__class__([to_utf8(x) for x in obj])
		else: pass
	except: pass
	return obj

def byteify(data, ignore_dicts=False):
	try:
		if isinstance(data, unicode):
			return data.encode('utf-8')
		if isinstance(data, list):
			return [byteify(item, ignore_dicts=True) for item in data]
		if isinstance(data, dict) and not ignore_dicts:
			return dict([(byteify(key, ignore_dicts=True), byteify(value, ignore_dicts=True)) for key, value in data.iteritems()])
	except: pass
	return data

def try_parse_int(string):
	'''helper to parse int from string without erroring on empty or misformed string'''
	try:
		return int(string)
	except Exception:
		return 0

def batch_replace(s, replace_info):
	for r in replace_info:
		s = str(s).replace(r[0], r[1])
	return s

def clean_file_name(s, use_encoding=False, use_blanks=True):
	try:
		hex_entities = [['&#x26;', '&'], ['&#x27;', '\''], ['&#xC6;', 'AE'], ['&#xC7;', 'C'],
					['&#xF4;', 'o'], ['&#xE9;', 'e'], ['&#xEB;', 'e'], ['&#xED;', 'i'],
					['&#xEE;', 'i'], ['&#xA2;', 'c'], ['&#xE2;', 'a'], ['&#xEF;', 'i'],
					['&#xE1;', 'a'], ['&#xE8;', 'e'], ['%2E', '.'], ['&frac12;', '%BD'],
					['&#xBD;', '%BD'], ['&#xB3;', '%B3'], ['&#xB0;', '%B0'], ['&amp;', '&'],
					['&#xB7;', '.'], ['&#xE4;', 'A'], ['\xe2\x80\x99', '']]
		special_encoded = [['"', '%22'], ['*', '%2A'], ['/', '%2F'], [':', ','], ['<', '%3C'],
							['>', '%3E'], ['?', '%3F'], ['\\', '%5C'], ['|', '%7C']]
		
		special_blanks = [['"', ' '], ['*', ' '], ['/', ' '], [':', ''], ['<', ' '],
							['>', ' '], ['?', ' '], ['\\', ' '], ['|', ' '], ['%BD;', ' '],
							['%B3;', ' '], ['%B0;', ' '], ["'", ""], [' - ', ' '], ['.', ' '],
							['!', '']]
		s = batch_replace(s, hex_entities)
		if use_encoding:
			s = batch_replace(s, special_encoded)
		if use_blanks:
			s = batch_replace(s, special_blanks)
		s = s.strip()
	except: pass
	return s

def clear_tvdb_token():
	set_setting('tvdb.jwtoken', '')
	set_setting('tvdb.jwtoken_expiry', '')
	open_settings('3.2')

def tmdbApi():
	return get_setting('tmdb_api', '1b0d3c6ac6a6c0fa87b55a1069d6c9c8')

def tvdbApi():
	return get_setting('tvdb_api', '905237D822EE21A6')

def tvdbJWToken():
	return get_setting('tvdb.jwtoken')

def get_fanart_data():
	return get_setting('get_fanart_data') == 'true'

def fanarttv_client_key():
	return get_setting('fanart_client_key')

def get_resolution():
	resolution = get_setting('image_resolutions')
	if resolution == '0': return {'poster': 'w185', 'fanart': 'w300', 'still': 'w92', 'profile': 'w185'}
	if resolution == '1': return {'poster': 'w342', 'fanart': 'w780', 'still': 'w185', 'profile': 'w185'}
	if resolution == '2': return {'poster': 'w780', 'fanart': 'w1280', 'still': 'w300', 'profile': 'h632'}
	if resolution == '3': return {'poster': 'original', 'fanart': 'original', 'still': 'original', 'profile': 'original'}
	else: return {'poster': 'w780', 'fanart': 'w1280', 'still': 'w185', 'profile': 'w185'}

def get_language():
	return get_setting('meta_language', 'en')

def user_info():
	tmdb_api = tmdbApi()
	tvdb_api = tvdbApi()
	tvdb_jwtoken = tvdbJWToken()
	extra_fanart_enabled = get_fanart_data()
	image_resolution = get_resolution()
	meta_language = get_language()
	if extra_fanart_enabled: fanart_client_key = fanarttv_client_key()
	else: fanart_client_key = ''
	return {'tmdb_api': tmdb_api, 'tvdb_api': tvdb_api, 'tvdb_jwtoken': tvdb_jwtoken, 'extra_fanart_enabled': extra_fanart_enabled,
			'fanart_client_key': fanart_client_key, 'image_resolution': image_resolution , 'language': meta_language}

def choose_language():
	import xbmcgui
	langs =     [
				# {'iso': 'default', 'name': 'Default'},
				{'iso': 'zh', 'name': 'Chinese'},
				{'iso': 'hr', 'name': 'Croatian'},
				{'iso': 'cs', 'name': 'Czech'},
				{'iso': 'da', 'name': 'Danish'},
				{'iso': 'nl', 'name': 'Dutch'},
				{'iso': 'en', 'name': 'English'},
				{'iso': 'fi', 'name': 'Finnish'},
				{'iso': 'fr', 'name': 'French'},
				{'iso': 'de', 'name': 'German'},
				{'iso': 'el', 'name': 'Greek'},
				{'iso': 'he', 'name': 'Hebrew'},
				{'iso': 'h', 'name': 'Hungarian'},
				{'iso': 'it', 'name': 'Italian'},
				{'iso': 'ja', 'name': 'Japanese'},
				{'iso': 'ko', 'name': 'Korean'},
				{'iso': 'no', 'name': 'Norwegian'},
				{'iso': 'pl', 'name': 'Polish'},
				{'iso': 'pt', 'name': 'Portuguese'},
				{'iso': 'ru', 'name': 'Russian'},
				{'iso': 'sl', 'name': 'Slovenian'},
				{'iso': 'es', 'name': 'Spanish'},
				{'iso': 'sv', 'name': 'Swedish'},
				{'iso': 'tr', 'name': 'Turkish'}
				]
	dialog = xbmcgui.Dialog()
	list_choose = dialog.select('Tikimeta - Choose Meta Language', [i['name'] for i in langs])
	if list_choose >= 0:
		chosen_language = langs[list_choose]['iso']
		# if chosen_language == 'default': chosen_language = xbmc.getLanguage(xbmc.ISO_639_1)
		chosen_language_display = langs[list_choose]['name']
		set_setting('meta_language', chosen_language)
		set_setting('meta_language_display', chosen_language_display)
		return True
	else: return False

def get_kodi_version():
	return int(xbmc.getInfoLabel("System.BuildVersion")[0:2])

def open_settings(query):
	try:
		xbmc.sleep(500)
		kodi_version = get_kodi_version()
		button = (-100) if kodi_version <= 17 else (100)
		control = (-200) if kodi_version <= 17 else (80)
		menu, function = query.split('.')
		xbmc.executebuiltin('Addon.OpenSettings(script.module.tikimeta)')
		xbmc.executebuiltin('SetFocus(%i)' % (int(menu) - button))
		xbmc.executebuiltin('SetFocus(%i)' % (int(function) - control))
	except: return




