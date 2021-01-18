# -*- coding: utf-8 -*-

import xbmc
import os
import json
from windows.base_dialog import BaseDialog
from windows.base_contextmenu import BaseContextMenu
from modules.utils import local_string as ls
from modules.settings import skin_location
# from modules.utils import logger

prerelease_quality = ('cam', 'tele', 'scr')
info_icons_dict = {'furk': 'furk.png', 'easynews': 'easynews.png', 'alldebrid': 'alldebrid.png',
					'real-debrid': 'realdebrid.png', 'premiumize': 'premiumize.png', 'ad-cloud': 'alldebrid.png',
					'rd-cloud': 'realdebrid.png', 'pm-cloud': 'premiumize.png'}

class SourceResultsXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		super(SourceResultsXML, self).__init__(self, args)
		self.window_style = kwargs.get('window_style', 'list default')
		self.window_id = kwargs.get('window_id')
		self.results = kwargs.get('results')
		self.meta = kwargs.get('meta')
		self.scraper_settings = kwargs.get('scraper_settings')
		self.prescrape = kwargs.get('prescrape')
		self.failed_results = []
		self.info = None
		self.cm = None

	def onInit(self):
		super(SourceResultsXML, self).onInit()
		self.make_items()
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.set_properties(self.meta, self.total_results)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		del self.info
		del self.cm
		return self.selected

	def get_provider_and_path(self, provider):
		if provider in info_icons_dict: provider_path = info_icons_dict[provider]
		else: provider_path = 'folders.png'
		return os.path.join(xbmc.translatePath('special://home/addons/script.module.tikiskins/resources/skins/Default/media/providers'), provider_path)

	def get_quality_and_path(self, quality):
		if quality in prerelease_quality: quality = 'sd'
		return os.path.join(xbmc.translatePath('special://home/addons/script.module.tikiskins/resources/skins/Default/media/flags'), '%s.png' % quality)

	def onAction(self, action):
		action_id = action.getId()
		if action_id in self.info_actions:
			chosen_listitem = self.item_list[self.get_position(self.window_id)]
			self.info = ResultsInfoXML('source_results.info.xml', skin_location(), item=chosen_listitem)
			self.info.run()
		if action_id in self.selection_actions:
			if self.prescrape:
				chosen_listitem = self.item_list[self.get_position(self.window_id)]
				if chosen_listitem.getProperty('tikiskins.perform_full_search') == 'true':
					self.selected = ('perform_full_search', '')
					return self.close()
			self.selected = ('play', self.item_results[self.get_position(self.window_id)])
			return self.close()
		elif action_id in self.context_actions:
			item_position = self.get_position(self.window_id)
			item = self.item_results[item_position]
			list_item = self.item_list[item_position]
			cache_provider = item.get('cache_provider', '')
			self.cm = ResultsContextMenuXML('contextmenu.xml', skin_location(), item=item, list_item=list_item, meta=self.meta, source_object=self)
			cm_choice = self.cm.run()
			if cm_choice:
				if 'results_info' in cm_choice:
					chosen_listitem = self.item_list[self.get_position(self.window_id)]
					self.info = ResultsInfoXML('source_results.info.xml', skin_location(), item=chosen_listitem)
					self.info.run()
				else:
					self.execute_code(cm_choice)
					# self.selected = (None, '')
					# return self.close()
		elif action_id in self.closing_actions:
			self.selected = (None, '')
			return self.close()

	def make_items(self):
		def builder():
			for count, item in enumerate(self.results, 1):
				try:
					listitem = self.make_listitem()
					scrape_provider = item['scrape_provider']
					source = item.get('source').upper()
					quality = item.get('quality', 'SD')
					quality_icon = self.get_quality_and_path(quality.lower())
					try: name = item.get('URLName', 'N/A').upper()
					except: name = 'N/A'
					pack = item.get('package', 'false') in ('true', 'show', 'season')
					if pack: extraInfo = '[B]PACK[/B] | %s' % item.get('extraInfo', '')
					else: extraInfo = item.get('extraInfo', '')
					if scrape_provider == 'external':
						source_site = item.get('name_rank').upper()
						provider = item.get('debrid', source_site).replace('.me', '').upper()
						provider_icon = self.get_provider_and_path(provider.lower())
						if 'cache_provider' in item:
							if 'Uncached' in item['cache_provider']:
								if 'seeders' in item: listitem.setProperty('tikiskins.source_type', 'UNCACHED (%d SEEDERS)' % item.get('seeders', 0))
								else: listitem.setProperty('tikiskins.source_type', 'UNCACHED')
								listitem.setProperty('tikiskins.highlight', 'white')
							else:
								if pack: listitem.setProperty('tikiskins.source_type', 'CACHED [B]PACK[/B]')
								else: listitem.setProperty('tikiskins.source_type', 'CACHED')
								listitem.setProperty('tikiskins.highlight', torrent_highlight)
						else:
							listitem.setProperty('tikiskins.source_type', source)
							listitem.setProperty('tikiskins.highlight', hoster_highlight)
						listitem.setProperty('tikiskins.name', name)
						listitem.setProperty('tikiskins.provider', provider)
						listitem.setProperty('tikiskins.source_site', source_site)
					else:
						provider_icon = self.get_provider_and_path(source.lower())
						highlight = '%s_highlight' % scrape_provider
						if 'folder' in scrape_provider:
							listitem.setProperty('tikiskins.highlight', self.scraper_settings['folders_highlight'])
							listitem.setProperty('tikiskins.folder_scraper', 'true')
						else: listitem.setProperty('tikiskins.highlight', self.scraper_settings[highlight])
						listitem.setProperty('tikiskins.name', name)
						listitem.setProperty('tikiskins.source_type', 'DIRECT')
						listitem.setProperty('tikiskins.provider', source)
						listitem.setProperty('tikiskins.source_site', source)
					listitem.setProperty('tikiskins.provider_icon', provider_icon)
					listitem.setProperty('tikiskins.quality_icon', quality_icon)
					listitem.setProperty('tikiskins.size_label', item.get('size_label', 'N/A'))
					listitem.setProperty('tikiskins.extra_info', extraInfo)
					listitem.setProperty('tikiskins.quality', quality.upper())
					listitem.setProperty('tikiskins.count', '%02d.' % count)
					listitem.setProperty('tikiskins.hash', item.get('hash', 'N/A'))
					yield listitem
				except:
					self.failed_results.append(item)
					pass
		try:
			hoster_highlight = self.scraper_settings['hoster_highlight']
			torrent_highlight = self.scraper_settings['torrent_highlight']			
			self.item_list = list(builder())
			if self.prescrape:
				prescrape_listitem = self.make_listitem()
				prescrape_listitem.setProperty('tikiskins.perform_full_search', 'true')
				prescrape_listitem.setProperty('tikiskins.start_full_scrape', '[B]***%s***[/B]' % ls(33023).upper())
			self.item_results = [i for i in self.results if not i in self.failed_results]
			self.total_results = str(len(self.item_results))
			if self.prescrape: self.item_list.append(prescrape_listitem)
		except: pass

	def set_properties(self, meta, total_results):
		self.setProperty('tikiskins.window_style', self.window_style)
		self.setProperty('tikiskins.fanart', self.meta['fanart'])
		self.setProperty('tikiskins.poster', self.meta['poster'])
		self.setProperty('tikiskins.clearlogo', self.meta['clearlogo'])
		self.setProperty('tikiskins.plot', self.meta['plot'])
		self.setProperty('tikiskins.total_results', self.total_results)

class ResultsInfoXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		super(ResultsInfoXML, self).__init__(self, args)
		self.item = kwargs['item']

	def run(self):
		self.set_properties()
		self.doModal()

	def onAction(self, action):
		action_id = action.getId()
		if action_id == 11: self.close()
		if action_id in self.closing_actions: self.close()

	def get_provider_and_path(self):
		provider = self.item.getProperty('tikiskins.provider').lower()
		if provider in info_icons_dict: provider_path = info_icons_dict[provider]
		else: provider_path = 'folders.png'
		return provider, os.path.join(xbmc.translatePath('special://home/addons/script.module.tikiskins/resources/skins/Default/media/providers'), provider_path)

	def get_quality_and_path(self):
		quality = self.item.getProperty('tikiskins.quality').lower()
		if quality in prerelease_quality: quality = 'sd'
		return quality, os.path.join(xbmc.translatePath('special://home/addons/script.module.tikiskins/resources/skins/Default/media/flags'), '%s.png' % quality)

	def set_properties(self):
		provider, provider_path = self.get_provider_and_path()
		quality, quality_path = self.get_quality_and_path()
		self.setProperty('tikiskins.results.info.name', self.item.getProperty('tikiskins.name'))
		self.setProperty('tikiskins.results.info.source_type', self.item.getProperty('tikiskins.source_type'))
		self.setProperty('tikiskins.results.info.source_site', self.item.getProperty('tikiskins.source_site'))
		self.setProperty('tikiskins.results.info.size_label', self.item.getProperty('tikiskins.size_label'))
		self.setProperty('tikiskins.results.info.extra_info', self.item.getProperty('tikiskins.extra_info'))
		self.setProperty('tikiskins.results.info.highlight', self.item.getProperty('tikiskins.highlight'))
		self.setProperty('tikiskins.results.info.hash', self.item.getProperty('tikiskins.hash'))
		self.setProperty('tikiskins.results.info.provider', provider)
		self.setProperty('tikiskins.results.info.quality', quality)
		self.setProperty('tikiskins.results.info.provider_icon', provider_path)
		self.setProperty('tikiskins.results.info.quality_icon', quality_path)

class ResultsContextMenuXML(BaseContextMenu):
	def __init__(self, *args, **kwargs):
		super(ResultsContextMenuXML, self).__init__(self, args)
		self.window_id = 2002
		self.item = kwargs['item']
		self.list_item = kwargs['list_item']
		self.meta = kwargs['meta']
		self.source_object = kwargs['source_object']
		self.item_list = []
		self.selected = None
		self.file_scrapers = ('folder1', 'folder2', 'folder3', 'folder4', 'folder5')

	def onInit(self):
		super(ResultsContextMenuXML, self).onInit()
		self.make_context_menu()
		self.set_properties()
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.selected

	def onAction(self, action):
		action_id = action.getId()
		if action_id in self.selection_actions:
			chosen_listitem = self.item_list[self.get_position(self.window_id)]
			self.selected = chosen_listitem.getProperty('tikiskins.context.action')
			return self.close()
		elif action_id in self.context_actions:
			return self.close()
		elif action_id in self.closing_actions:
			return self.close()
	
	def set_properties(self):
		highlight = self.list_item.getProperty('tikiskins.highlight')
		self.setProperty('tikiskins.context.highlight', highlight)

	def make_context_menu(self):
		down_str, extra_info_str, browse_str, browse_debrid_str, addto_str, down_archive_str = ls(32747), ls(32605), ls(32811), ls(33004), ls(32769), ls(32982)
		meta_json = json.dumps(self.meta)
		title = self.item.get('title')
		item_id = self.item.get('id', None)
		name = self.item.get('name')
		url_dl = self.item.get('url_dl')
		scrape_provider = self.item.get('scrape_provider')
		cache_provider = self.item.get('cache_provider', 'None')
		uncached_torrent = True if 'Uncached' in cache_provider else False
		source = json.dumps([self.item])
		
		self.item_list.append(self.make_item('[B]%s[/B]' % extra_info_str, 'RunPlugin(%s)', {'mode': 'results_info'}))
		
		if not uncached_torrent and scrape_provider not in self.file_scrapers:
			down_file_params = {'mode': 'downloader',
								'action': 'meta.single',
								'name': self.meta.get('rootname', ''),
								'source': source,
								'url': None,
								'provider': scrape_provider,
								'meta': meta_json}
			self.item_list.append(self.make_item(down_str, 'RunPlugin(%s)', down_file_params))
			

			if 'package' in self.item and not scrape_provider == 'furk':
				browse_debrid_pack_params = {'mode': 'browse_debrid_pack',
											'provider': cache_provider,
											'name': name,
											'magnet_url': self.item['url'],
											'info_hash': self.item['hash']}
				down_arch_params = {'mode': 'downloader',
								'action': 'meta.pack',
								'name': self.meta.get('rootname', ''),
								'source': source,
								'url': None,
								'provider': scrape_provider,
								'meta': meta_json}
				self.item_list.append(self.make_item(browse_debrid_str, 'RunPlugin(%s)', browse_debrid_pack_params))
			

			elif scrape_provider == 'furk':
				add_files_params = {'mode': 'furk.add_to_files',
									'item_id': item_id}
				if self.item.get('package', 'false') == 'true':
					import os
					from modules.settings import get_theme
					default_furk_icon = os.path.join(get_theme(), 'furk.png')
					

					browse_pack_params = {'mode': 'furk.browse_packs',
										'file_name': name,
										'file_id': item_id}
					

					down_arch_params = {'mode': 'downloader',
									'db_type': 'furk.pack',
									'action': 'furk.pack',
									'name': self.meta.get('rootname', ''),
									'source': source,
									'url': url_dl,
									'provider': scrape_provider,
									'image': default_furk_icon}
					# self.item_list.append(self.make_item(down_archive_str,'RunPlugin(%s)', down_arch_params))
					self.item_list.append(self.make_item(browse_str, 'RunPlugin(%s)', browse_pack_params))
				self.item_list.append(self.make_item(addto_str, 'RunPlugin(%s)', add_files_params))

