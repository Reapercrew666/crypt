# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

import os.path
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET

addon = xbmcaddon.Addon
addonObject = addon('script.module.fenomscrapers')
addonInfo = addonObject.getAddonInfo
getLangString = addonObject.getLocalizedString
condVisibility = xbmc.getCondVisibility
execute = xbmc.executebuiltin
jsonrpc = xbmc.executeJSONRPC
monitor = xbmc.Monitor()

dialog = xbmcgui.Dialog()
window = xbmcgui.Window(10000)

existsPath = xbmcvfs.exists
openFile = xbmcvfs.File
makeFile = xbmcvfs.mkdir
joinPath = os.path.join

SETTINGS_PATH = xbmc.translatePath(os.path.join(addonInfo('path'), 'resources', 'settings.xml'))

try:
	dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
except:
	dataPath = xbmc.translatePath(addonInfo('profile'))

cacheFile = os.path.join(dataPath, 'cache.db')


def setting(id):
	return xbmcaddon.Addon('script.module.fenomscrapers').getSetting(id)


def setSetting(id, value):
	return xbmcaddon.Addon('script.module.fenomscrapers').setSetting(id, value)


def sleep(time):  # Modified `sleep` command that honors a user exit request
	while time > 0 and not monitor.abortRequested():
		xbmc.sleep(min(100, time))
		time = time - 100


def getKodiVersion():
	return int(xbmc.getInfoLabel("System.BuildVersion")[:2])


def lang(language_id):
	text = getLangString(language_id)
	if getKodiVersion() < 19:
		text = text.encode('utf-8', 'replace')
	return text


def check_version_numbers(current, new):
	# Compares version numbers and return True if new version is newer
	current = current.split('.')
	new = new.split('.')
	step = 0
	for i in current:
		if int(new[step]) > int(i):
			return True
		if int(i) == int(new[step]):
			step += 1
			continue
	return False


def isVersionUpdate():
	versionFile = os.path.join(dataPath, 'installed.version')
	try:
		if not xbmcvfs.exists(versionFile):
			f = open(versionFile, 'w')
			f.close()
	except:
		xbmc.log('FenomScrapers Addon Data Path Does not Exist. Creating Folder....', 2)
		addon_folder = xbmc.translatePath('special://profile/addon_data/script.module.fenomscrapers')
		xbmcvfs.mkdirs(addon_folder)
	try:
		with open(versionFile, 'rb') as fh:
			oldVersion = fh.read()
	except:
		oldVersion = '0'
	try:
		curVersion = addon('script.module.fenomscrapers').getAddonInfo('version')
		if oldVersion != curVersion:
			with open(versionFile, 'wb') as fh:
				fh.write(curVersion)
			return True
		else:
			return False
	except:
		import traceback
		traceback.print_exc()
		return False


def clean_settings():
	def _make_content(dict_object):
		if kodi_version >= 18:
			content = '<settings version="2">'
			for item in dict_object:
				if item['id'] in active_settings:
					if 'default' in item and 'value' in item: content += '\n    <setting id="%s" default="%s">%s</setting>' % (item['id'], item['default'], item['value'])
					elif 'default' in item: content += '\n    <setting id="%s" default="%s"></setting>' % (item['id'], item['default'])
					elif 'value' in item: content += '\n    <setting id="%s">%s</setting>' % (item['id'], item['value'])
					else: content += '\n    <setting id="%s"></setting>'
				else: removed_settings.append(item)
		else:
			content = '<settings>'
			for item in dict_object:
				if item['id'] in active_settings:
					if 'value' in item: content += '\n    <setting id="%s" value="%s" />' % (item['id'], item['value'])
					else: content += '\n    <setting id="%s" value="" />' % item['id']
				else: removed_settings.append(item)
		content += '\n</settings>'
		return content
	kodi_version = getKodiVersion()
	addon_id = 'script.module.fenomscrapers'
	try:
		removed_settings = []
		active_settings = []
		current_user_settings = []
		addon = xbmcaddon.Addon(id=addon_id)
		addon_name = addon.getAddonInfo('name')
		addon_dir = xbmc.translatePath(addon.getAddonInfo('path'))
		profile_dir = xbmc.translatePath(addon.getAddonInfo('profile'))
		active_settings_xml = os.path.join(addon_dir, 'resources', 'settings.xml')
		root = ET.parse(active_settings_xml).getroot()
		for item in root.findall(r'./category/setting'):
			setting_id = item.get('id')
			if setting_id:
				active_settings.append(setting_id)
		settings_xml = os.path.join(profile_dir, 'settings.xml')
		root = ET.parse(settings_xml).getroot()
		for item in root:
			dict_item = {}
			setting_id = item.get('id')
			setting_default = item.get('default')
			if kodi_version >= 18:
				setting_value = item.text
			else: setting_value = item.get('value')
			dict_item['id'] = setting_id
			if setting_value:
				dict_item['value'] = setting_value
			if setting_default:
				dict_item['default'] = setting_default
			current_user_settings.append(dict_item)
		new_content = _make_content(current_user_settings)
		nfo_file = xbmcvfs.File(settings_xml, 'w')
		nfo_file.write(new_content)
		nfo_file.close()
		sleep(200)
		notification(title=addon_name, message=lang(32042).format(str(len(removed_settings))))
	except:
		import traceback
		traceback.print_exc()
		notification(title=addon_name, message=32043)


def addonId():
	return addonInfo('id')


def addonName():
	return addonInfo('name')


def addonVersion():
	return addonInfo('version')


def addonIcon():
	return addonInfo('icon')


def openSettings(query=None, id=addonInfo('id')):
	try:
		idle()
		execute('Addon.OpenSettings(%s)' % id)
		if not query: return
		c, f = query.split('.')
		if getKodiVersion() >= 18:
			execute('SetFocus(%i)' % (int(c) - 100))
			execute('SetFocus(%i)' % (int(f) - 80))
		else:
			execute('SetFocus(%i)' % (int(c) + 100))
			execute('SetFocus(%i)' % (int(f) + 200))
	except:
		return


def getSettingDefault(id):
	import re
	try:
		settings = open(SETTINGS_PATH, 'r')
		value = ' '.join(settings.readlines())
		value.strip('\n')
		settings.close()
		value = re.findall(r'id=\"%s\".*?default=\"(.*?)\"' % (id), value)[0]
		return value
	except:
		return None


def idle():
	if getKodiVersion() >= 18 and condVisibility('Window.IsActive(busydialognocancel)'):
		return execute('Dialog.Close(busydialognocancel)')
	else:
		return execute('Dialog.Close(busydialog)')


def notification(title=None, message=None, icon=None, time=3000, sound=False):
	if title == 'default' or title is None:
		title = addonName()
	if isinstance(title, (int, long)):
		heading = lang(title)
	else:
		heading = str(title)
	if isinstance(message, (int, long)):
		body = lang(message)
	else:
		body = str(message)
	if icon is None or icon == '' or icon == 'default':
		icon = addonIcon()
	elif icon == 'INFO':
		icon = xbmcgui.NOTIFICATION_INFO
	elif icon == 'WARNING':
		icon = xbmcgui.NOTIFICATION_WARNING
	elif icon == 'ERROR':
		icon = xbmcgui.NOTIFICATION_ERROR
	dialog.notification(heading, body, icon, time, sound=sound)


def syncMyAccounts(silent=False):
	import myaccounts
	all_acct = myaccounts.getAllScraper()

	fp_acct = all_acct.get('filepursuit')
	if setting('filepursuit.api') != fp_acct.get('api_key'):
		setSetting('filepursuit.api', fp_acct.get('api_key'))

	fu_acct = all_acct.get('furk')
	if setting('furk.user_name') != fu_acct.get('username'):
		setSetting('furk.user_name', fu_acct.get('username'))
		setSetting('furk.user_pass', fu_acct.get('password'))
	if fu_acct.get('api_key', None):
		if setting('furk.api') != fu_acct.get('api_key'):
			setSetting('furk.api', fu_acct.get('api_key'))

	en_acct = all_acct.get('easyNews')
	if setting('easynews.user') != en_acct.get('username'):
		setSetting('easynews.user', en_acct.get('username'))
		setSetting('easynews.password', en_acct.get('password'))

	gd_acct = all_acct.get('gdrive')
	if setting('gdrive.cloudflare_url') != gd_acct.get('url'):
		setSetting('gdrive.cloudflare_url', gd_acct.get('url'))

	or_acct = all_acct.get('ororo')
	if setting('ororo.user') != or_acct.get('email'):
		setSetting('ororo.user', or_acct.get('email'))
		setSetting('ororo.pass', or_acct.get('password'))

	if not silent: notification(message=32038)