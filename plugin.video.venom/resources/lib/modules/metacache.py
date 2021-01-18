# -*- coding: utf-8 -*-
'''
	Venom Add-on
'''

import time
try: from sqlite3 import dbapi2 as db
except ImportError: from pysqlite2 import dbapi2 as db

from resources.lib.modules import control
from resources.lib.modules import log_utils


def fetch(items, lang='en', user=''):
	if not control.existsPath(control.dataPath):
		control.makeFile(control.dataPath)
	dbcon = db.connect(control.metacacheFile)
	dbcur = dbcon.cursor()
	ck_table = dbcur.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='meta';''').fetchone()
	if not ck_table:
		dbcur.execute('''CREATE TABLE IF NOT EXISTS meta (imdb TEXT, tmdb TEXT, tvdb TEXT, lang TEXT, user TEXT, item TEXT, time TEXT,
		UNIQUE(imdb, tmdb, tvdb, lang, user));''')
		dbcur.connection.commit()
		dbcur.close() ; dbcon.close()
		return items
	t2 = int(time.time())
	for i in range(0, len(items)):
		try:
			try: # First lookup by TVDb and IMDb, since there are some incorrect shows on Trakt that have the same IMDb ID, but different TVDb IDs (eg: Gotham, Supergirl).
				match = dbcur.execute('''SELECT * FROM meta WHERE (imdb=? AND tvdb=? AND lang=? AND user=? AND NOT imdb='0' AND NOT tvdb='0')''',
					(items[i].get('imdb', '0'), items[i].get('tvdb', '0'), lang, user)).fetchone()
				t1 = int(match[6])
			except:
				try: # Lookup both IMDb and TMDb for more accurate match.
					match = dbcur.execute('''SELECT * FROM meta WHERE (imdb=? AND tmdb=? AND lang=? AND user=? AND not imdb='0' AND NOT tmdb='0')''',
						(items[i].get('imdb', '0'), items[i].get('tmdb', '0'), lang, user)).fetchone()
					t1 = int(match[6])
				except:
					try: # Last resort single ID lookup.
						match = dbcur.execute('''SELECT * FROM meta WHERE (imdb=? AND lang=? AND user=? AND NOT imdb='0') OR (tmdb=? AND lang=? AND user=? AND NOT tmdb='0') OR (tvdb=? AND lang=? AND user=? AND NOT tvdb='0')''',
							(items[i].get('imdb', '0'), lang, user, items[i].get('tmdb', '0'), lang, user, items[i].get('tvdb', '0'), lang, user)).fetchone()
						t1 = int(match[6])
					except: pass
			if match:
				update = (abs(t2 - t1) / 3600) >= 720
				if update: continue
				item = eval(match[5].encode('utf-8'))
				item = dict((k, v) for k, v in item.iteritems() if v != '0')
				items[i].update(item)
				items[i].update({'metacache': True})
		except:
			log_utils.error()
	try: dbcur.close() ; dbcon.close()
	except: pass
	return items


def insert(meta):
	try:
		if not control.existsPath(control.dataPath):
			control.makeFile(control.dataPath)
		dbcon = db.connect(control.metacacheFile)
		dbcur = dbcon.cursor()
		dbcur.execute('''CREATE TABLE IF NOT EXISTS meta (imdb TEXT, tmdb TEXT, tvdb TEXT, lang TEXT, user TEXT, item TEXT, time TEXT,
		UNIQUE(imdb, tmdb, tvdb, lang, user));''')
		t = int(time.time())
		for m in meta:
			if "user" not in m: m["user"] = ''
			if "lang" not in m: m["lang"] = 'en'
			i = repr(m['item'])
			try: dbcur.execute('''INSERT OR REPLACE INTO meta Values (?, ?, ?, ?, ?, ?, ?)''', (m.get('imdb', '0'), m.get('tmdb', '0'), m.get('tvdb', '0'), m['lang'], m['user'], i, t))
			except: pass
		dbcur.connection.commit()
	except:
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()