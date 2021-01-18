# -*- coding: utf-8 -*-
import xbmc, xbmcgui
# from modules.utils import logger

class BaseDialog(xbmcgui.WindowXMLDialog):
	def __init__(self, *args):
		xbmcgui.WindowXMLDialog.__init__(self, args)
		self.closing_actions = [9, 10, 13, 92]
		self.selection_actions = [7, 100]
		self.context_actions = [101, 117]
		self.info_actions = [11,]

	def make_listitem(self):
		return xbmcgui.ListItem()

	def execute_code(self, command):
		return xbmc.executebuiltin(command)
	
	def get_position(self, window_id):
		return self.getControl(window_id).getSelectedPosition()
