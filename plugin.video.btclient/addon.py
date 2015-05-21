'''
Created on May 15, 2015

@author: ivan
'''
import sys
import os.path
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
sys.path.append(os.path.join(os.path.split(__file__)[0],'resources/lib'))
from plugin import *

addon = xbmcaddon.Addon()
download_dir=addon.getSetting('download_dir')
delete_on_finish=bool( addon.getSetting('delete_on_finish') == 'true')
clear_older=int(addon.getSetting('clear_older'))
debug= bool(addon.getSetting('debug')=='true')

base,handle,params=parse_args()

print 'PLUGIN arguments',sys.argv
print 'Download dir', download_dir
print 'Debug enabled?', debug



if not download_dir:
    xbmcgui.Dialog().notification('Settings Error!', 'Download directory is not set', 
                                  xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable

action=params.get('action')
print 'Action =', action
if not action:
    
#     url = 'http://localhost:8888/video.mp4'
#     li = xbmcgui.ListItem('Test Video!', iconImage='DefaultVideo.png')
#     xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li)
    xbmcplugin.addDirectoryItem(handle, build_url(base,action='search'), 
                            xbmcgui.ListItem('Search'), isFolder=True)
    xbmcplugin.addDirectoryItem(handle, download_dir, 
                            xbmcgui.ListItem('Downloaded files'), isFolder=True)
    for s in search_history(addon):
        xbmcplugin.addDirectoryItem(handle, build_url(base,action='search', query=s), 
                            xbmcgui.ListItem(s), isFolder=True)
    
elif action==['search']:
    print 'SEARCH'
    if not params.get('query'):
        phrase=kbd_input(heading='Enter Search phrase')
    else:
        phrase=params.get('query')[0]
    search(base,phrase)
    add_to_search_history(addon, phrase)
    
elif action==['play']:
    url=resolve(params.get('source')[0], params.get('url')[0])
    print 'PLAY', url
    play(download_dir,url, debug=debug, delete_on_finish=delete_on_finish, clear_older=clear_older)

if (handle>=0):
    xbmcplugin.endOfDirectory(handle)

