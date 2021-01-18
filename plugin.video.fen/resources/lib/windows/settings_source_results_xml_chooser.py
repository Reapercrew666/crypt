# -*- coding: utf-8 -*-
import xbmc
from windows.base_dialog import BaseDialog
# from modules.utils import logger

class SettingsResultsXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		super(SettingsResultsXML, self).__init__(self, args)
		self.window_id = 5001
		self.xml_choices = kwargs.get('xml_choices')
		self.xml_items = []

	def onInit(self):
		super(SettingsResultsXML, self).onInit()
		self.make_items()
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.xml_items)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.choice

	def onAction(self, action):
		action_id = action.getId()
		if action_id in self.closing_actions:
			self.choice = None
			self.close()
		if action_id in self.selection_actions:
			chosen_listitem = self.xml_items[self.get_position(self.window_id)]
			self.choice = chosen_listitem.getProperty('tikiskins.window.name')
			self.close()

	def make_items(self):
		for item in self.xml_choices:
			listitem = self.make_listitem()
			listitem.setProperty('tikiskins.window.image', item[0])
			listitem.setProperty('tikiskins.window.name', item[1])
			self.xml_items.append(listitem)
