# -*- coding: utf-8 -*-
'''
	Venom Add-on
'''

from resources.lib.modules import control
from resources.lib.modules import log_utils

window = control.homeWindow
plugin = 'plugin://plugin.video.venom/'


class CheckSettingsFile:
	def run(self):
		try:
			control.log('[ plugin.video.venom ]  CheckSettingsFile Service Starting...', 2)
			window.clearProperty('venom_settings')
			profile_dir = control.dataPath
			if not control.existsPath(profile_dir):
				success = control.makeDirs(profile_dir)
				if success: control.log('%s : created successfully' % profile_dir, 2)
			else: control.log('%s : already exists' % profile_dir, 2)
			settings_xml = control.joinPath(profile_dir, 'settings.xml')
			if not control.existsPath(settings_xml):
				control.setSetting('trakt.message1', '')
				control.log('%s : created successfully' % settings_xml, 2)
			else: control.log('%s : already exists' % settings_xml, 2)
			return control.log('[ plugin.video.venom ]  Finished CheckSettingsFile Service', 2)
		except:
			log_utils.error()


class SettingsMonitor(control.monitor_class):
	def __init__ (self):
		control.monitor_class.__init__(self)
		control.log('[ plugin.video.venom ]  Settings Monitor Service Starting...', 2)


	def onSettingsChanged(self):
		# Kodi callback when the addon settings are changed
		window.clearProperty('venom_settings')
		control.sleep(50)
		refreshed = control.make_settings_dict()


class SyncMyAccounts:
	def run(self):
		control.log('[ plugin.video.venom ]  Sync "My Accounts" Service Starting...', 2)
		control.syncMyAccounts(silent=True)
		return control.log('[ plugin.video.venom ]  Finished Sync "My Accounts" Service', 2)


class ReuseLanguageInvokerCheck:
	def run(self):
		if control.getKodiVersion() < 18: return
		control.log('[ plugin.video.venom ]  ReuseLanguageInvokerCheck Service Starting...', 2)
		try:
			import xml.etree.ElementTree as ET
			addon_xml = control.joinPath(control.addonPath('plugin.video.venom'), 'addon.xml')
			tree = ET.parse(addon_xml)
			root = tree.getroot()
			current_addon_setting = control.addon('plugin.video.venom').getSetting('reuse.languageinvoker')
			try: current_xml_setting = [str(i.text) for i in root.iter('reuselanguageinvoker')][0]
			except: return control.log('[ plugin.video.venom ]  ReuseLanguageInvokerCheck failed to get settings.xml value', 2)
			if current_addon_setting == '':
				current_addon_setting = 'true'
				control.setSetting('reuse.languageinvoker', current_addon_setting)
			if current_xml_setting == current_addon_setting:
				return control.log('[ plugin.video.venom ]  ReuseLanguageInvokerCheck Service Finished', 2)
			control.okDialog(message='%s\n%s' % (control.lang(33023), control.lang(33020)))
			for item in root.iter('reuselanguageinvoker'):
				item.text = current_addon_setting
				hash_start = control.gen_file_hash(addon_xml)
				tree.write(addon_xml)
				hash_end = control.gen_file_hash(addon_xml)
				control.log('[ plugin.video.venom ]  ReuseLanguageInvokerCheck Service Finished', 2)
				if hash_start != hash_end:
					current_profile = control.infoLabel('system.profilename')
					control.execute('LoadProfile(%s)' % current_profile)
				else: control.okDialog(title='default', message=33022)
			return
		except:
			log_utils.error()


class AddonCheckUpdate:
	def run(self):
		control.log('[ plugin.video.venom ]  Addon checking available updates', 2)
		try:
			import re
			import requests
			repo_xml = requests.get('https://raw.githubusercontent.com/123Venom/zips/master/addons.xml')
			if not repo_xml.status_code == 200:
				control.log('[ plugin.video.venom ]  Could not connect to remote repo XML: status code = %s' % repo_xml.status_code, 2)
				return
			repo_version = re.findall(r'<addon id=\"plugin.video.venom\".+version=\"(\d*.\d*.\d*)\"', repo_xml.text)[0]
			local_version = control.getVenomVersion()
			if control.check_version_numbers(local_version, repo_version):
				while control.condVisibility('Library.IsScanningVideo'):
					control.sleep(10000)
				control.log('[ plugin.video.venom ]  A newer version is available. Installed Version: v%s, Repo Version: v%s' % (local_version, repo_version), 2)
				control.notification(message=control.lang(35523) % repo_version)
			return control.log('[ plugin.video.venom ]  Addon update check complete', 2)
		except:
			log_utils.error()


class LibraryService:
	def run(self):
		control.log('[ plugin.video.venom ]  Library Update Service Starting (Update check every 6hrs)...', 2)
		control.execute('RunPlugin(%s?action=library_service)' % plugin) # library_service contains control.monitor().waitForAbort() while loop every 6hrs


class SyncTraktCollection:
	def run(self):
		control.log('[ plugin.video.venom ]  Trakt Collection Sync Starting...', 2)
		control.execute('RunPlugin(%s?action=library_tvshowsToLibrarySilent&url=traktcollection)' % plugin)
		control.execute('RunPlugin(%s?action=library_moviesToLibrarySilent&url=traktcollection)' % plugin)
		control.log('[ plugin.video.venom ]  Trakt Collection Sync Complete', 2)


class SyncTraktWatched:
	def run(self):
		control.log('[ plugin.video.venom ]  Trakt Watched Sync Service Starting (sync check every 15min)...', 2)
		control.execute('RunPlugin(%s?action=tools_syncTraktWatched)' % plugin) # trakt.sync_watched() contains control.monitor().waitForAbort() while loop every 15min


class SyncTraktProgress:
	def run(self):
		control.log('[ plugin.video.venom ]  Trakt Progress Sync Service Starting (sync check every 15min)...', 2)
		control.execute('RunPlugin(%s?action=tools_syncTraktProgress)' % plugin) # trakt.sync_progress() contains control.monitor().waitForAbort() while loop every 15min


try:
	AddonVersion = control.addon('plugin.video.venom').getAddonInfo('version')
	RepoVersion = control.addon('repository.venom').getAddonInfo('version')
	log_utils.log('#####   CURRENT VENOM VERSIONS REPORT   #####', log_utils.LOGNOTICE)
	log_utils.log('########   VENOM PLUGIN VERSION: %s   ########' % str(AddonVersion), log_utils.LOGNOTICE)
	log_utils.log('#####   VENOM REPOSITORY VERSION: %s   #######' % str(RepoVersion), log_utils.LOGNOTICE)
except:
	log_utils.log('################# CURRENT Venom VERSIONS REPORT ################', log_utils.LOGNOTICE)
	log_utils.log('# ERROR GETTING Venom VERSION - Missing Repo of failed Install #', log_utils.LOGNOTICE)


def getTraktCredentialsInfo():
	username = control.setting('trakt.username').strip()
	token = control.setting('trakt.token')
	refresh = control.setting('trakt.refresh')
	if (username == '' or token == '' or refresh == ''): return False
	return True


def main():
	while not control.monitor.abortRequested():
		control.log('[ plugin.video.venom ]  Service Started', 2)
		syncWatched = None
		syncProgress = None
		schedTrakt = None
		libraryService = None
		CheckSettingsFile().run()
		SyncMyAccounts().run()
		ReuseLanguageInvokerCheck().run()
		if control.setting('library.service.update') == 'true':
			libraryService = True
			LibraryService().run()
		if control.setting('general.checkAddonUpdates') == 'true':
			AddonCheckUpdate().run()
		if getTraktCredentialsInfo():
			if control.setting('indicators.alt') == '1':
				syncWatched = True
				SyncTraktWatched().run()
			if control.setting('bookmarks') == 'true' and control.setting('resume.source') == '1':
				syncProgress = True
				SyncTraktProgress().run()
			if control.setting('autoTraktOnStart') == 'true':
				SyncTraktCollection().run()
			if int(control.setting('schedTraktTime')) > 0:
				import threading
				log_utils.log('#################### STARTING TRAKT SCHEDULING ################', log_utils.LOGNOTICE)
				log_utils.log('#################### SCHEDULED TIME FRAME '+ control.setting('schedTraktTime')  + ' HOURS ###############', log_utils.LOGNOTICE)
				timeout = 3600 * int(control.setting('schedTraktTime'))
				schedTrakt = threading.Timer(timeout, SyncTraktCollection().run) # this only runs once at the designated interval time to wait...not repeating
				schedTrakt.start()
		break
	SettingsMonitor().waitForAbort()
	control.log('[ plugin.video.venom ]  Settings Monitor Service Stopping...', 2)
	if syncWatched:
		control.log('[ plugin.video.venom ]  Trakt Watched Sync Service Stopping...', 2)
	if syncProgress:
		control.log('[ plugin.video.venom ]  Trakt Progress Sync Service Stopping...', 2)
	if libraryService:
		control.log('[ plugin.video.venom ]  Library Update Service Stopping...', 2)
	if schedTrakt:
		schedTrakt.cancel()
		# control.log('[ plugin.video.venom ]  Trakt Collection Sync Stopping...', 2)
	control.log('[ plugin.video.venom ]  Service Stopped', 2)

main()