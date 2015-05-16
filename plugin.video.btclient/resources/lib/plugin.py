'''
Created on May 15, 2015

@author: ivan
'''
import sys
import urlparse
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import os.path

from sources import ulozto
from runner import Client
from player import MyPlayer
import time
from contextlib import closing

def parse_args(args=None):
    args=args or sys.argv
    base=args[0]
    handle=int(args[1])
    params = urlparse.parse_qs(args[2][1:])
    return base, handle, params


def build_url(base, **query):
    return base + '?' + urllib.urlencode(query)

def kbd_input(default=u"", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
            return unicode( keyboard.getText(), "utf-8" )
    return default    

def add_item(name,url,iconimage=''):
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok  

def search(base,kw):  
    res=ulozto.search(kw)   
    for r in res:
        url=build_url(base, action='play', url=r['url'], source='ulozto')
        add_item(r.get('title') or r.get('name',''), url, r.get('img') or r.get('icon',''))
        
def resolve(src,url):
    print 'Resolving %s' %src
    if src=='ulozto':
        
        return ulozto.resolve(url)
    
    return url

def debug(s):
    print s
    
    
def play(download_dir, url,item=None, debug=False):
    print "URL is", url, 'Dir is', download_dir
    with closing(Client(download_dir, os.path.join(download_dir, 'btclient.log') if debug else None)) as c:
        with closing(xbmcgui.DialogProgress()) as d:
            d.create('Preloading', 'Loading video from stream ...')
            d.update(0)
            print 'Starting client'
            c.start(url)   
            print 'Client running with pid %d' % c.pid
            started=time.time()
            while not c.poll_ready(1):
                if xbmc.abortRequested or d.iscanceled():  # @UndefinedVariable
                    return
                # As we cannot say exact progress - just updated according to time for now
                tick=min(100,int((time.time()-started)*2))
                d.update(tick,*c.status.split('\n')[:3])
            c.wait_ready()  
            d.update(100) 
            print "Got link %s" % c.link
            
        with closing(MyPlayer()) as p:
            p.play(c.link)
            while p.isPlaying():
                    p.update_status(lambda:c.status)
                    xbmc.sleep(1000)    
        print '######### Exiting play'
        

HISTORY_SIZE=20        
        
def search_history(addon):
    h=addon.getSetting('search_history')
    if h:
        return h.split('||')
    return []

def add_to_search_history(addon, s):
    if not s:
        return
    l= search_history(addon)
    if s in l:
        l.remove(s)
    l.insert(0, s)
    if len(s)>HISTORY_SIZE:
        l.pop()
    addon.setSetting('search_history', '||'.join(l))
    
    
    

    