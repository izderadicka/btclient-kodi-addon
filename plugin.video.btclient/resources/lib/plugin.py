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

from runner import Client
from player import MyPlayer
import time
from contextlib import closing
import sources
from threading import Thread
import traceback

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


def combine(ll):
    pos=0
    while True:
        any=False
        for l in ll:
            if len(l)>pos:
                yield l[pos]
                any=True
        if not any:
            break
        pos+=1
            

def search(base,kw):  
    res=[]
    def s(p,q):
        def add_src(i):
            i['source']=p.__name__
        try: 
            r=p.search(q)
            map(add_src,r)
            res.append(r)
        except Exception,e:
            print "Search in plugin %s failed with %s " % (p.__name__, e)
            traceback.print_exc()
    threads=[]    
    for p in sources.plugs:
        threads.append(Thread(target=s, args=(p,kw)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for r in combine(res):
        print r
        url=build_url(base, action='play', url=r['url'], source=r['source'])
        add_item(r.get('title') or r.get('name',''), url, r.get('img') or r.get('icon',''))
        
def resolve(src,url):
    print 'Resolving %s' %src
    return sources.resolve(src, url)

def debug(s):
    print s
    
    
def play(download_dir, url,item=None, debug=False, delete_on_finish=False, clear_older=0,
         bt_download_limit=0, bt_upload_limit=0):
    print "URL is", url, 'Dir is', download_dir
    with closing(Client(download_dir, os.path.join(download_dir, 'btclient.log') if debug else None, 
                 delete_on_finish=delete_on_finish, clear_older=clear_older,
                 bt_download_limit=bt_download_limit, bt_upload_limit=bt_upload_limit)) as c:
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
    s=s.encode('utf8',errors='ignore') if isinstance(s, unicode) else s
    l= search_history(addon)
    if s in l:
        l.remove(s)
    l.insert(0, s)
    if len(s)>HISTORY_SIZE:
        l.pop()
    addon.setSetting('search_history', '||'.join(l))
    
    
    

    