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

def debug(s):
    print s
    
def error(s):
    raise Exception(s)

def substr(data,start,end):
    i1 = data.find(start)
    i2 = data.find(end,i1)
    return data[i1:i2]


UA='Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'

def request(url,headers={}):
    debug('request: %s' % url)
    req = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    debug('len(data) %s' % len(data))
    return data

def post_json(url,data,headers={}):
    postdata = json.dumps(data)
    headers['Content-Type'] = 'application/json'
    req = urllib2.Request(url,postdata,headers)
    req.add_header('User-Agent',UA)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    return data


def resolve(url):
        if url.startswith('#'):
            ret = json.loads(request(url[1:]))
            if ret.has_key('result'):
                url = b64decode(ret['result'])
                url=urlparse.urljoin(BASE, url)
                
            else:
                print 'Ulozto - decrypt problem'
        return url
    
BASE= 'http://uloz.to/'   
def search(query):
    url=BASE+'hledej/?media=video&type=size__desc&q='+urllib.quote(query)
    page = request(url,headers={'X-Requested-With':'XMLHttpRequest','Referer':url,'Cookie':'uloz-to-id=1561277170;'})
    script = substr(page,'var kn','</script>')
    keymap = None
    key = None
    k = re.search('{([^\;]+)"',script,re.IGNORECASE | re.DOTALL)
    if k:
        keymap = json.loads("{"+k.group(1)+"\"}")
    j = re.search('kapp\(kn\[\"([^\"]+)"',script,re.IGNORECASE | re.DOTALL)
    if j:
        key = j.group(1)
    if not (j and k):
        error('error parsing page - unable to locate keys')
        return []
    burl = b64decode('I2h0dHA6Ly9kZWNyLWNlY2gucmhjbG91ZC5jb20vZGVjcnlwdC8/a2V5PSVzJnZhbHVlPSVz')
    murl = b64decode('aHR0cDovL2RlY3ItY2VjaC5yaGNsb3VkLmNvbS9kZWNyeXB0Lw==')
    data = substr(page,'<ul class=\"chessFiles','</ul>') 
    result = []
    req = {'seed':keymap[key],'values':keymap}
    decr = json.loads(post_json(murl,req))
    for li in re.finditer('<li data-icon=\"(?P<key>[^\"]+)',data, re.IGNORECASE |  re.DOTALL):
        body = urllib.unquote(b64decode(decr[li.group('key')]))
        m = re.search('<li>.+?<div data-icon=\"(?P<key>[^\"]+)[^<]+<img(.+?)src=\"(?P<logo>[^\"]+)(.+?)<div class=\"fileInfo(?P<info>.+?)</h4>',body, re.IGNORECASE |  re.DOTALL)
        if not m:
            continue
        value = keymap[m.group('key')]
        info = m.group('info')
        iurl = burl % (keymap[key],value)
        item = {}
        item['title'] = '.. title not found..'
        title = re.search('<div class=\"fileName.+?<a[^>]+>(?P<title>[^<]+)',info, re.IGNORECASE|re.DOTALL)
        if title:
            item['title'] = title.group('title')
        size = re.search('<span class=\"fileSize[^>]+>(?P<size>[^<]+)',info, re.IGNORECASE|re.DOTALL)
        if size:
            item['size'] = size.group('size').strip()
            item['title']+=' (%s)'%item['size']
        time = re.search('<span class=\"fileTime[^>]+>(?P<time>[^<]+)',info, re.IGNORECASE|re.DOTALL)
        if time:
            item['length'] = time.group('time')
        item['url'] = iurl
        item['img'] = m.group('logo')
        result.append(item)
    # page navigation
#     data = util.substr(page,'<div class=\"paginator','</div')
#     mnext = re.search('<a href=\"(?P<url>[^\"]+)\" class="next',data)
#     if mnext:
#         item = self.dir_item()
#         item['type'] = 'next'
#         item['url'] = mnext.group('url')
#         result.append(item)
    debug('Ulozto found %d items'%(len(result),))
    return result