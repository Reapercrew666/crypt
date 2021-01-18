# -*- coding: utf-8 -*-
'''
	Venom Add-on
'''

import ast
from hashlib import md5
import re
import time
try: from sqlite3 import dbapi2 as db
except ImportError: from pysqlite2 import dbapi2 as db

from resources.lib.modules import control
from resources.lib.modules import log_utils


def get(function, duration, *args):
	"""
	:param function: Function to be executed
	:param duration: Duration of validity of cache in hours
	:param args: Optional arguments for the provided function
	"""
	try:
		key = _hash_function(function, args)
		cache_result = cache_get(key)
		if cache_result:
			try: result = ast.literal_eval(cache_result['value'].encode('utf-8'))
			except: result = ast.literal_eval(cache_result['value'])
			if _is_cache_valid(cache_result['date'], duration):
				return result

		fresh_result = repr(function(*args))
		try:  # Sometimes None is returned as a string instead of None type for "fresh_result"
			invalid = False
			if not fresh_result: invalid = True
			elif fresh_result == 'None' or fresh_result == '' or fresh_result == '[]' or fresh_result == '{}': invalid = True
			elif len(fresh_result) == 0: invalid = True
		except: pass

		if invalid: # If the cache is old, but we didn't get "fresh_result", return the old cache
			if cache_result: return result
			else: return None
		else:
			cache_insert(key, fresh_result)
			try: return ast.literal_eval(fresh_result.encode('utf-8'))
			except: result = ast.literal_eval(fresh_result)
	except:
		log_utils.error()
		return None


def remove(function, *args):
	try:
		key = _hash_function(function, args)
		key_exists = cache_get(key)
		if key_exists:
			cursor = _get_connection_cursor()
			cursor.execute('''DELETE FROM cache WHERE key=?''', (key,))
			cursor.connection.commit()
	except:
		log_utils.error()
	try: cursor.close()
	except: pass


def timeout(function, *args):
	try:
		key = _hash_function(function, args)
		result = cache_get(key)
		return int(result['date']) if result else 0
	except:
		log_utils.error()
		return 0


def cache_existing(function, *args):
	try:
		cache_result = cache_get(_hash_function(function, args))
		if cache_result:
			try: return ast.literal_eval(cache_result['value'].encode('utf-8'))
			except: return ast.literal_eval(cache_result['value']) # fails
		else: return None
	except:
		log_utils.error()
		return None


def cache_get(key):
	try:
		cursor = _get_connection_cursor()
		ck_table = cursor.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='cache';''').fetchone()
		if not ck_table: return None
		results = cursor.execute('''SELECT * FROM cache WHERE key=?''', (key,)).fetchone()
		return results
	except:
		log_utils.error()
		return None
	finally:
		cursor.close()


def cache_insert(key, value):
	try:
		cursor = _get_connection_cursor()
		now = int(time.time())
		cursor.execute('''CREATE TABLE IF NOT EXISTS cache (key TEXT, value TEXT, date INTEGER, UNIQUE(key));''')
		update_result = cursor.execute('''UPDATE cache SET value=?,date=? WHERE key=?''', (value, now, key))
		if update_result.rowcount is 0:
			cursor.execute('''INSERT INTO cache Values (?, ?, ?)''', (key, value, now))
		cursor.connection.commit()
	except:
		log_utils.error()
	finally:
		cursor.close()


def cache_version_check():
	if _find_cache_version():
		cache_clear_all()
		control.notification(message=32057)


def cache_clear_all():
	try:
		cache_clear_providers()
		cache_clear_meta()
		cache_clear()
		cache_clear_search()
		cache_clear_bookmarks()
		return True
	except:
		log_utils.error()


def cache_clear_providers():
	cursor = _get_connection_cursor_providers()
	for t in ['cache', 'rel_src', 'rel_url']:
		try:
			cursor.execute('''DROP TABLE IF EXISTS {}'''.format(t))
			cursor.execute('''VACUUM''')
			cursor.connection.commit()
		except:
			log_utils.error()
	cursor.close()
	return True


def cache_clear_meta():
	cursor = _get_connection_cursor_meta()
	try:
		cursor.execute('''DROP TABLE IF EXISTS meta''')
		cursor.execute('''VACUUM''')
		cursor.connection.commit()
		return True
	except:
		log_utils.error()
	finally:
		cursor.close()


def cache_clear():
	cursor = _get_connection_cursor()
	for t in ['cache', 'rel_list', 'rel_lib']:
		try:
			cursor.execute('''DROP TABLE IF EXISTS {}'''.format(t))
			cursor.execute('''VACUUM''')
			cursor.connection.commit()
		except:
			log_utils.error()
	cursor.close()
	return True


def cache_clear_search():
	cursor = _get_connection_cursor_search()
	for t in ['tvshow', 'movies']:
		try:
			cursor.execute('''DROP TABLE IF EXISTS {}'''.format(t))
			cursor.execute('''VACUUM''')
			cursor.connection.commit()
			control.refresh()
		except:
			log_utils.error()
	cursor.close()
	return True


def cache_clear_SearchPhrase(table, key):
	cursor = _get_connection_cursor_search()
	try:
		cursor.execute('''DELETE FROM {} WHERE term=?;'''.format(table), (key,))
		cursor.connection.commit()
		control.refresh()
		return True
	except:
		log_utils.error()
	finally:
		cursor.close()


def cache_clear_bookmarks():
	cursor = _get_connection_cursor_bookmarks()
	try:
		cursor.execute('''DROP TABLE IF EXISTS bookmark''')
		cursor.execute('''VACUUM''')
		cursor.connection.commit()
		return True
	except:
		log_utils.error()
	finally:
		cursor.close()


def cache_clear_bookmark(name, year='0'):
	cursor = _get_connection_cursor_bookmarks()
	# idFile = md5()
	# for i in name:
		# idFile.update(str(i))
	# for i in year:
		# idFile.update(str(i))
	# idFile = str(idFile.hexdigest())
	years = [str(year), str(int(year)+1), str(int(year)-1)]
	try:
		# cursor.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
		cursor.execute('''DELETE FROM bookmark WHERE Name="%s" AND year IN (%s)''' % (name, ','.join(i for i in years)))
		cursor.connection.commit()
		control.refresh()
		control.trigger_widget_refresh()
		return True
	except:
		log_utils.error()
	finally:
		cursor.close()


def clear_local_bookmarks(): # clear all venom bookmarks from kodi database
	conn = db.connect(control.get_video_database_path())
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT * FROM files WHERE strFilename LIKE '%plugin.video.venom%'")
		file_ids = [str(i[0]) for i in cursor.fetchall()]
		for table in ["bookmark", "streamdetails", "files"]:
			cursor.execute("DELETE FROM {} WHERE idFile IN ({})".format(table, ','.join(file_ids)))
		cursor.connection.commit()
	except:
		log_utils.error()
	finally:
		cursor.close() ; conn.close()


def clear_local_bookmark(url): # clear all item specific bookmarks from kodi database
	conn = db.connect(control.get_video_database_path())
	cursor = conn.cursor()
	try:
		cursor.execute('SELECT * FROM files WHERE strFilename LIKE "%{}%"'.format(url))
		file_ids = [str(i[0]) for i in cursor.fetchall()]
		if not file_ids:
			return
		for table in ["bookmark", "streamdetails", "files"]:
			cursor.execute("DELETE FROM {} WHERE idFile IN ({})".format(table, ','.join(file_ids)))
		cursor.connection.commit()
	except:
		log_utils.error()
	finally:
		cursor.close() ; conn.close()


def _get_connection_cursor():
	conn = _get_connection()
	return conn.cursor()


def _get_connection():
	control.makeFile(control.dataPath)
	conn = db.connect(control.cacheFile)
	conn.row_factory = _dict_factory
	return conn


def _get_connection_cursor_meta():
	conn = _get_connection_meta()
	return conn.cursor()


def _get_connection_meta():
	control.makeFile(control.dataPath)
	conn = db.connect(control.metacacheFile)
	conn.row_factory = _dict_factory
	return conn


def _get_connection_cursor_providers():
	conn = _get_connection_providers()
	return conn.cursor()


def _get_connection_providers():
	control.makeFile(control.dataPath)
	conn = db.connect(control.providercacheFile)
	conn.row_factory = _dict_factory
	return conn


def _get_connection_cursor_search():
	conn = _get_connection_search()
	return conn.cursor()


def _get_connection_search():
	control.makeFile(control.dataPath)
	conn = db.connect(control.searchFile)
	conn.row_factory = _dict_factory
	return conn


def _get_connection_cursor_bookmarks():
	conn = _get_connection_bookmarks()
	return conn.cursor()


def _get_connection_bookmarks():
	control.makeFile(control.dataPath)
	conn = db.connect(control.bookmarksFile)
	conn.row_factory = _dict_factory
	return conn


def _dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


def _hash_function(function_instance, *args):
	return _get_function_name(function_instance) + _generate_md5(args)


def _get_function_name(function_instance):
	return re.sub(r'.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(function_instance))


def _generate_md5(*args):
	md5_hash = md5()
	try: [md5_hash.update(str(arg)) for arg in args]
	except: [md5_hash.update(str(arg).encode('utf-8')) for arg in args]
	return str(md5_hash.hexdigest())


def _is_cache_valid(cached_time, cache_timeout):
	now = int(time.time())
	diff = now - cached_time
	return (cache_timeout * 3600) > diff


def _find_cache_version():
	versionFile = control.joinPath(control.dataPath, 'cache.v')
	try:
		if not control.existsPath(versionFile):
			f = open(versionFile, 'w')
			f.close()
	except:
		log_utils.log('Venom Addon Data Path Does not Exist. Creating Folder....', __name__, log_utils.LOGDEBUG)
		ad_folder = control.transPath('special://profile/addon_data/plugin.video.venom')
		control.makeDirs(ad_folder)
	try:
		with open(versionFile, 'rb') as fh:
			oldVersion = fh.read()
	except:
		oldVersion = '0'
	try:
		curVersion = control.addon('plugin.video.venom').getAddonInfo('version')
		if oldVersion != curVersion:
			with open(versionFile, 'wb') as fh:
				fh.write(curVersion)
			return True
		else:
			return False
	except:
		log_utils.error()
		return False