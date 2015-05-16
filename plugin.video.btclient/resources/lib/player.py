'''
Created on May 15, 2015

@author: ivan
'''


import xbmc, xbmcgui
import os.path
import sys


RESOURCES_PATH=os.path.join(os.path.dirname(sys.modules["__main__"].__file__), 'resources')
WINDOW_FULLSCREEN_VIDEO = 12005
VIEWPORT_WIDTH = 1920.0
VIEWPORT_HEIGHT = 1088.0

#this class in borrowed from XBMCTorrent
class OverlayText(object):
    def __init__(self, w, h, *args, **kwargs):
        self.window = xbmcgui.Window(WINDOW_FULLSCREEN_VIDEO)
        viewport_w, viewport_h = self._get_skin_resolution()
        # Adjust size based on viewport, we are using 1080p coordinates
        w = int(w * viewport_w / VIEWPORT_WIDTH)
        h = int(h * viewport_h / VIEWPORT_HEIGHT)
        x = (viewport_w - w) / 2
        y = (viewport_h - h) / 2
        self._shown = False
        self._text = ""
        self._label = xbmcgui.ControlLabel(x, y, w, h, self._text, *args, **kwargs)
        self._background = xbmcgui.ControlImage(x, y, w, h, os.path.join(RESOURCES_PATH, "media", "black.png"))
        self._background.setColorDiffuse("0xD0000000")

    def show(self):
        if not self._shown:
            self.window.addControls([self._background, self._label])
            self._shown = True

    def hide(self):
        if self._shown:
            self._shown = False
            self.window.removeControls([self._background, self._label])

    def close(self):
        self.hide()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        if self._shown:
            self._label.setLabel(self._text)
            
    @property
    def is_shown(self):
        return self._shown

    # This is so hackish it hurts.
    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = xbmc.translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])

class MyPlayer(xbmc.Player):
    
    def __init__(self):
        xbmc.Player.__init__(self)
        self._overlay=OverlayText(900,200)
        
    def onPlayBackPaused(self):
        xbmc.log('PLAYER - Playback paused')
        self._overlay.show()
       
    def onPlayBackResumed(self):
        xbmc.log('PLAYER - Playback resumed')
        self._overlay.hide()
        
    def onPlayBackEnded(self):
        xbmc.log('PLAYER - Playback ended')
        self._overlay.hide()
        
    def onPlayBackStopped(self):
        xbmc.log('PLAYER - Playback stopped')
        self._overlay.hide()
        
    def onPlayBackStarted(self):
        xbmc.log('PLAYER - Playback started')
        
    def close(self):
        self._overlay.close()
        
    def update_status(self, fn):
        if self._overlay.is_shown:
            self._overlay.text=fn()