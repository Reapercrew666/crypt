from resources.lib.plugin import Plugin
from resources.lib.util.xml import JenList
import random
import xbmc


class Rainbow(Plugin):
    name = "rainbow"
    priority = 200

    def process_item(self, item_xml):
        if "<rainbow>" not in item_xml:
            color = "%06x" % random.randint(0, 0xFFFFFF)
            if "<name>" in item_xml:
                            item_xml = item_xml.replace("<name>", "<name>[B][COLOR]YTT - [/COLOR][/B] [COLOR FFff%s][B]" % color,
                                        1)
                            item_xml = item_xml.replace("</name>", "[/B][/COLOR]</name>", 1)
            else:
                item_xml = item_xml.replace("<title>", "<title>[B][COLOR]YTT - [/COLOR][/B] [COLOR FFff%s][B]" % color,
                                            1)
                item_xml = item_xml.replace("</title>", "[/B][/COLOR]</title>", 1)
            item_xml += "<rainbow></rainbow>"
            return JenList(item_xml).process_item(item_xml)
