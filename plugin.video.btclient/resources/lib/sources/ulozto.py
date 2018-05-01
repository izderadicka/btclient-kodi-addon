'''
Created on May 15, 2015

@author: ivan
'''

#Ulozto search is extracted from plugin.video.online-files from XBMC doplnky project
import urllib
from base64 import b64decode
import urllib2
import re
import json
import urlparse
import os
try:
    from  .. import phantomjs
except (ImportError, ValueError):
    import phantomjs
    

def debug(s):
    print s
    
def error(s):
    raise Exception(s)

def substr(data,start,end):
    i1 = data.find(start)
    i2 = data.find(end,i1)
    return data[i1:i2]


UA='Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
class RedirectFilter(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        return None    

no_redirect_opener = urllib2.build_opener(RedirectFilter)

def redirect(url,headers={}):
    debug('request: %s' % url)
    headers['User-Agent'] = UA
    req = urllib2.Request(url,headers=headers)
    try:
        no_redirect_opener.open(req)
    except urllib2.HTTPError as e:
        if e.code == 301:
            new_url = e.headers['Location']
            parsed_url = urlparse.urlsplit(new_url)
            if parsed_url.path.startswith('/!'):
                return new_url
    


def resolve(url):
    return redirect(url)
    
BASE= 'https://uloz.to/'   
PHANTOM = phantomjs.JSEngine(os.path.join(os.path.dirname(__file__), '../../data/ulozto.js'), 15)
def search(query):
    #&type=size__desc 
    url=BASE+'hledej/?type=videos&q='+urllib.quote(query)
    res = PHANTOM.eval(url)
    res = json.loads(res)
    res = filter(lambda i: 'name' in i and 'url' in i, res)
    if res[0]['name'] == 'mtbr.avi':
        res=res[1:]
    for i in res:
        if 'size' in i:
            i['name'] = i['name']+ ' (%s)'% i['size']
        i['url'] = urlparse.urljoin(BASE, i['url'])
        i['img'] = urlparse.urljoin(BASE, i['img'])
        
    return res
    

if __name__ == '__main__':
    res= search('duchacek')
    mp4_file = filter(lambda x: x['name'].find('.mp4')>=0, res)[0]
    print mp4_file["name"]
    print resolve(mp4_file['url'])
    