# -*- coding: utf-8 -*-
'''
	Venom Add-on
'''

from datetime import datetime
try: from sqlite3 import dbapi2 as db
except ImportError: from pysqlite2 import dbapi2 as db

from resources.lib.modules import cleandate
from resources.lib.modules import control
from resources.lib.modules import log_utils


def fetch_bookmarks(imdb, tmdb='', tvdb='', season=None, episode=None):
	progress = '0'
	try:
		if not control.existsPath(control.dataPath):
			control.makeFile(control.dataPath)
		dbcon = db.connect(control.traktSyncFile)
		dbcur = dbcon.cursor()
		ck_table = dbcur.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='bookmarks';''').fetchone()
		if not ck_table:
			dbcur.execute('''CREATE TABLE IF NOT EXISTS bookmarks (imdb TEXT, tmdb TEXT, tvdb TEXT, season TEXT, episode TEXT, percent_played TEXT, paused_at TEXT,
			UNIQUE(imdb, tmdb, tvdb, season, episode));''')
			dbcur.connection.commit()
			dbcur.close() ; dbcon.close()
			return progress
		if not episode:
			try: # Lookup both IMDb and TMDb first for more accurate match.
				match = dbcur.execute('''SELECT * FROM bookmarks WHERE (imdb=? AND tmdb=? AND NOT imdb='' AND NOT tmdb='')''', (imdb, tmdb)).fetchone()
				progress = match[5]
			except:
				try:
					match = dbcur.execute('''SELECT * FROM bookmarks WHERE (imdb=? AND NOT imdb='')''', (imdb,)).fetchone()
					progress = match[5]
				except: pass
		else:
			try: # Lookup both IMDb and TVDb first for more accurate match.
				match = dbcur.execute('''SELECT * FROM bookmarks WHERE (imdb=? AND tvdb=? AND season=? AND episode=? AND NOT imdb='' AND NOT tvdb='')''', (imdb, tvdb, season, episode)).fetchone()
				progress = match[5]
			except:
				try:
					match = dbcur.execute('''SELECT * FROM bookmarks WHERE (tvdb=? AND season=? AND episode=? AND NOT tvdb='')''', (tvdb, season, episode)).fetchone()
					progress = match[5]
				except: pass
	except:
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()
	return progress


def insert_bookmarks(items, new_scrobble=False):
	try:
		if not control.existsPath(control.dataPath):
			control.makeFile(control.dataPath)
		dbcon = db.connect(control.traktSyncFile)
		dbcur = dbcon.cursor()
		dbcur.execute('''CREATE TABLE IF NOT EXISTS bookmarks (imdb TEXT, tmdb TEXT, tvdb TEXT, season TEXT, episode TEXT, percent_played TEXT, paused_at TEXT,
		UNIQUE(imdb, tmdb, tvdb, season, episode));''')
		dbcur.execute('''CREATE TABLE IF NOT EXISTS service (setting TEXT, value TEXT, UNIQUE(setting));''')
		if not new_scrobble:
			dbcur.execute('''DELETE FROM bookmarks''')
			dbcur.execute('''VACUUM''')
		for i in items:
			imdb, tmdb, tvdb, season, episode = '', '', '', '', ''
			if i.get('type') == 'episode':
				ids = i.get('show').get('ids')
				imdb, tmdb, tvdb, season, episode = str(ids.get('imdb', '')), str(ids.get('tmdb', '')), str(ids.get('tvdb', '')), str(i.get('episode').get('season')), str(i.get('episode').get('number'))
			else:
				ids = i.get('movie').get('ids')
				imdb, tmdb = str(ids.get('imdb', '')), str(ids.get('tmdb', ''))
			dbcur.execute('''INSERT OR REPLACE INTO bookmarks Values (?, ?, ?, ?, ?, ?, ?)''', (imdb, tmdb, tvdb, season, episode, i.get('progress', ''), i.get('paused_at', '')))
		timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
		dbcur.execute('''INSERT OR REPLACE INTO service Values (?, ?)''', ('last_paused_at', timestamp))
		dbcur.connection.commit()
	except:
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()


def delete_bookmark(items):
	try:
		if not control.existsPath(control.dataPath):
			control.makeFile(control.dataPath)
		dbcon = db.connect(control.traktSyncFile)
		dbcur = dbcon.cursor()
		ck_table = dbcur.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='bookmarks';''').fetchone()
		if not ck_table:
			dbcur.execute('''CREATE TABLE IF NOT EXISTS bookmarks (imdb TEXT, tmdb TEXT, tvdb TEXT, season TEXT, episode TEXT, percent_played TEXT, paused_at TEXT,
			UNIQUE(imdb, tmdb, tvdb, season, episode));''')
			dbcur.execute('''CREATE TABLE IF NOT EXISTS service (setting TEXT, value TEXT, UNIQUE(setting));''')
			dbcur.connection.commit()
			return
		for i in items:
			if i.get('type') == 'episode':
				ids = i.get('show').get('ids')
				imdb, tvdb, season, episode, = str(ids.get('imdb', '')), str(ids.get('tvdb', '')), str(i.get('episode').get('season')), str(i.get('episode').get('number'))
			else:
				tvdb, season, episode = '', '', ''
				ids = i.get('movie').get('ids')
				imdb = str(ids.get('imdb', ''))
			try:
				dbcur.execute('''DELETE FROM bookmarks WHERE (imdb=? AND tvdb=? AND season=? AND episode=?)''', (imdb, tvdb, season, episode))
				dbcur.execute('''INSERT OR REPLACE INTO service Values (?, ?)''', ('last_paused_at', i.get('paused_at', '')))
				dbcur.connection.commit()
			except: pass
	except:
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()


def last_paused_at():
	last_paused = 0
	try:
		if not control.existsPath(control.dataPath):
			control.makeFile(control.dataPath)
		dbcon = db.connect(control.traktSyncFile)
		dbcur = dbcon.cursor()
		ck_table = dbcur.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='service';''').fetchone()
		if ck_table:
			match = dbcur.execute('''SELECT * FROM service WHERE setting="last_paused_at";''').fetchone()
			if match: last_paused = int(cleandate.iso_2_utc(match[1]))
			else: dbcur.execute('''INSERT OR REPLACE INTO service Values (?, ?)''', ('last_paused_at', '1970-01-01T20:00:00.000Z'))
		else: dbcur.execute('''CREATE TABLE IF NOT EXISTS service (setting TEXT, value TEXT, UNIQUE(setting));''')
	except:
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()
	return last_paused