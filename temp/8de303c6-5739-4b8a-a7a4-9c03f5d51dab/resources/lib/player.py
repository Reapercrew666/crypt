import json
import time

from kodi_six import xbmc
from threading import Thread

from slyguy import userdata, inputstream
from slyguy.util import get_kodi_string, set_kodi_string
from slyguy.log import log

from .monitor import monitor

class Player(xbmc.Player):
    # def __init__(self, *args, **kwargs):
    #     self._thread = None
    #     self._up_next = None
    #     self._callback = None
    #     super(Player, self).__init__(*args, **kwargs)

    def playback(self, playing_file):
        last_callback = None
        cur_time = time.time()
        play_time = 0

        while not monitor.waitForAbort(1) and self.isPlaying() and self.getPlayingFile() == playing_file:
            cur_time  = time.time()
            play_time = self.getTime()

            if self._up_next and play_time >= self._up_next['time']:
                play_time = self.getTotalTime()
                self.seekTime(play_time)
                last_callback = None

            if self._callback and self._callback['type'] == 'interval' and (not last_callback or cur_time >= last_callback + self._callback['interval']):
                callback = self._callback['callback'].replace('%24playback_time', str(int(play_time))).replace('$playback_time', str(int(play_time)))
                xbmc.executebuiltin('RunPlugin({})'.format(callback))
                last_callback = cur_time

        if self._callback:
            callback = self._callback['callback'].replace('%24playback_time', str(int(play_time))).replace('$playback_time', str(int(play_time)))
            xbmc.executebuiltin('RunPlugin({})'.format(callback))

    def onAVStarted(self):
        self._up_next = None
        self._callback = None
        self._thread = Thread(target=self.playback, args=(self.getPlayingFile(),))
        self._thread.start()

        up_next = get_kodi_string('_slyguy_play_next')
        if up_next:
            set_kodi_string('_slyguy_play_next')
            up_next = json.loads(up_next)
            if up_next['playing_file'] == self.getPlayingFile():
                if up_next['next_file']:
                    if self.isPlayingVideo():
                        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                    else:
                        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
                    
                    playlist.remove(up_next['next_file'])
                    playlist.add(up_next['next_file'], index=playlist.getposition()+1)

                if up_next['time']:
                    self._up_next = up_next

        callback = get_kodi_string('_slyguy_play_callback')
        if callback:
            set_kodi_string('_slyguy_play_callback')
            callback = json.loads(callback)
            if callback['playing_file'] == self.getPlayingFile() and callback['callback']:
                self._callback = callback

    # def onPlayBackEnded(self):
    #     vid_playlist   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    #     music_playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    #     position       = vid_playlist.getposition()+1

    #     if (vid_playlist.size() <= 1 or vid_playlist.size() == position) and (music_playlist.size() <= 1 or music_playlist.size() == position):
    #         self.onPlayBackStopped()

    # def onPlayBackStopped(self):
    #     set_kodi_string('_slyguy_last_quality')

    # def onPlayBackStarted(self):
    #     pass

    # def onPlayBackPaused(self):
    #     print("AV PAUSED")
            
    # def onPlayBackResumed(self):
    #     print("AV RESUME")

    # def onPlayBackError(self):
    #     self.onPlayBackStopped()