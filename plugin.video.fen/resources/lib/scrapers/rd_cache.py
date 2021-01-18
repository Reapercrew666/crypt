# -*- coding: utf-8 -*-
from threading import Thread
from apis.real_debrid_api import RealDebridAPI
from caches import fen_cache
from modules.source_utils import get_release_quality, get_file_info, supported_video_extensions
from modules.utils import clean_title, clean_file_name, normalize
from scrapers import internal_results
from modules.settings import debrid_enabled
# from modules.utils import logger

RealDebrid = RealDebridAPI()
_cache = fen_cache.FenCache()

class RealDebridSource:
	def __init__(self):
		self.scrape_provider = 'rd-cloud'
		self.enabled = debrid_enabled('rd')
		self.sources = []
		self.folder_results = []
		self.scrape_results = []

	def results(self, info):
		try:
			if not self.enabled: return internal_results(self.scrape_provider, self.sources)
			self.info = info
			self.db_type = self.info.get("db_type")
			self.title = self.info.get("title")
			self.year = self.info.get("year")
			if self.year: self.rootname = '%s (%s)' % (self.title, self.year)
			else: self.rootname = self.title
			self.season = self.info.get("season", None)
			self.episode = self.info.get("episode", None)
			self.extensions = supported_video_extensions()
			self.folder_query = clean_title(normalize(self.title))
			self.query_list = self._year_query_list() if self.db_type == 'movie' else self._episode_query_list()
			self._scrape_cloud()
			self._scrape_downloads()
			if not self.scrape_results: return internal_results(self.scrape_provider, self.sources)
			def _process():
				for item in self.scrape_results:
					try:
						direct_debrid_link = item.get('direct_debrid_link', False)
						folder_name = normalize(item['folder_name'])
						file_name = self._get_filename(item['path'])
						URLName = clean_file_name(file_name).replace('html', ' ').replace('+', ' ').replace('-', ' ')
						file_dl = item['url_link']
						size = float(item['bytes'])/1073741824
						video_quality = get_release_quality(file_name, folder_name)
						details = get_file_info(file_name)
						if not details: details = get_file_info(folder_name)
						source_item = {'name': file_name,
										'title': file_name,
										'URLName': URLName,
										'quality': video_quality,
										'size': size,
										'size_label': '%.2f GB' % size,
										'extraInfo': details,
										'url_dl': file_dl,
										'id': file_dl,
										'downloads': False,
										'direct': True,
										'source': self.scrape_provider,
										'scrape_provider': self.scrape_provider,
										'direct_debrid_link': direct_debrid_link}
						yield source_item
					except: pass
			self.sources = list(_process())
		except Exception as e:
			from modules.utils import logger
			logger('FEN real-debrid scraper Exception', e)
		internal_results(self.scrape_provider, self.sources)
		return self.sources

	def _assigned_content(self, raw_name):
		try:
			string = 'FEN_RD_%s' % raw_name
			return _cache.get(string)
		except:
			return False

	def _scrape_cloud(self):
		try:
			try: my_cloud_files = RealDebrid.user_cloud()
			except: return self.sources
			for item in my_cloud_files:
				folder_name = clean_title(normalize(item['filename']))
				assigned_content = self._assigned_content(normalize(item['filename']))
				if assigned_content:
					if assigned_content == self.rootname:
						self.folder_results.append((normalize(item['filename']), item['id'], True))
				elif self.folder_query in folder_name or not folder_name:
					self.folder_results.append((normalize(item['filename']), item['id'], False))
			if not self.folder_results: return self.sources
			threads = []
			for i in self.folder_results: threads.append(Thread(target=self._scrape_folders, args=(i,)))
			[i.start() for i in threads]
			[i.join() for i in threads]
		except: pass

	def _scrape_folders(self, folder_info):
		try:
			assigned_folder = folder_info[2]
			folder_files = RealDebrid.user_cloud_info(folder_info[1])
			file_info = [i for i in folder_files['files'] if i['path'].lower().endswith(tuple(self.extensions))]
			file_urls = folder_files['links']
			for c, i in enumerate(file_info):
				try: i.update({'folder_name': folder_info[0], 'url_link': file_urls[c]})
				except: pass
			contents = sorted(file_info, key=lambda k: k['path'])
			for item in contents:
				filename = clean_title(normalize(item['path']))
				if assigned_folder and self.db_type == 'movie':
						self.scrape_results.append(item)
				elif any(x in filename for x in self.query_list):
					if assigned_folder:
						self.scrape_results.append(item)
					elif self.folder_query in filename:
						self.scrape_results.append(item)
		except: pass

	def _scrape_downloads(self):
		try:
			my_downloads = RealDebrid.downloads()
			my_downloads = [i for i in my_downloads if i['download'].lower().endswith(tuple(self.extensions))]
			for item in my_downloads:
				filename = clean_title(normalize(item['filename']))
				if any(x in filename for x in self.query_list):
					if self.folder_query in filename:
						item = self.make_history_item(item)
						if item['path'] not in [d['path'] for d in self.scrape_results]:
							self.scrape_results.append(item)
		except: pass

	def make_history_item(self, history_item):
		finished_item = {}
		finished_item['folder_name'] = history_item['filename']
		finished_item['url_link'] = history_item['download']
		finished_item['bytes'] = history_item['filesize']
		finished_item['path'] = history_item['filename']
		finished_item['direct_debrid_link'] = True
		return finished_item

	def _year_query_list(self):
		return [str(self.year), str(int(self.year)+1), str(int(self.year)-1)]

	def _episode_query_list(self):
		return ['s%02de%02d' % (int(self.season), int(self.episode)),
				'%dx%02d' % (int(self.season), int(self.episode)),
				'%02dx%02d' % (int(self.season), int(self.episode)),
				'season%02depisode%02d' % (int(self.season), int(self.episode)),
				'season%depisode%02d' % (int(self.season), int(self.episode)),
				'season%depisode%d' % (int(self.season), int(self.episode))]

	def _get_filename(self, name):
		if name.startswith('/'): name = name.split('/')[-1]
		return clean_file_name(normalize(name))



