'''
Created on Nov 1, 2015

@author: ivan
'''

import urllib
import urllib2
import re

BASE_URL="http://btdigg.org/search"
flags=re.UNICODE|re.IGNORECASE|re.DOTALL
SEARCH_RES=re.compile('<div id=\"search_res\">(.+)', flags)
ITEM_RE=re.compile(r'table class="torrent_name_tbl".*?<td class="torrent_name"><a.*?>(?P<name>.*?)</a>.*?href="(?P<url>magnet:[^"]+).*?Size:</span><span class="attr_val">(?P<size>[^<]+).*?Files:</span><span class="attr_val">(?P<files>[^<]+).*?<pre class="snippet">(?P<snip>.+?)</pre>',
                   flags)
VIDEO_RE= re.compile(r'\.(mkv|avi|mp4)', re.UNICODE)


def search(query):
    found=[]
    for p in range(2):
        q=urllib.urlencode({'q':query, 'p':p, 'order':1})
        req=urllib2.Request(BASE_URL+'?'+q)
        req.add_header('User-Agent', "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0")
        res=urllib2.urlopen(req, timeout=10)
        html=res.read()
        m=SEARCH_RES.search(html)
        if m:
            for n in ITEM_RE.finditer(m.group(1)):
                d={}
                d['title']= n.group('name')
                d['url']=  n.group('url')
                d['size']= n.group('size').replace('&nbsp;', '')
                d['title']+= ' (%s)'%d['size']
                is_video=bool(VIDEO_RE.search(n.group('snip')))
                if is_video:
                    found.append(d)
    return found
    
    

def resolve(url):
    return url


if __name__=='__main__':
    print search('terminator')

