'''
Created on May 20, 2015

@author: ivan
'''
import urllib
import urllib2
import json

BASE_URL='https://yts.am/api/v2/list_movies.json'
class ApiError(Exception):
    pass

def query_json(query):
    q=urllib.urlencode({'query_term':query})
    req = urllib2.Request(BASE_URL+"?"+q,
    headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0"})
    res=urllib2.urlopen(req, timeout=10)
    res=json.load(res)
    if res['status'] != 'ok':
        raise ApiError('Error response from API: %s - %s'%(res['status'],res['status_message']))
    return res['data']


def search(query):
    data= query_json(query)
    res=[]
    for m in data['movies'] if data['movie_count']>0 else []:
        title=m['title'] + (' (%s)' % m['year'])
        thumb=m['medium_cover_image']
        qualities = [t["quality"] for t in m['torrents']]
        desired_quality = '1080p' if '1080p' in qualities else '720p'
        for t in m['torrents']:
            if t["quality"] != desired_quality:
                continue
            d={}
            d['size']=t['size']
            d['img']=thumb
            d['title']=title + (' (%s)[%s]' % (t['size'], t['quality']))
            d['url']=t['url']
            res.append(d)
    return res

def resolve(url):
    return url


if __name__=='__main__':
    print search('terminator')