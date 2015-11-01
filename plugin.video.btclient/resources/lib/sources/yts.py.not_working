'''
Created on May 20, 2015

@author: ivan
'''
import urllib
import urllib2
import json

BASE_URL='https://yts.to/api/v2/list_movies.json'
class ApiError(Exception):
    pass

def query_json(query):
    q=urllib.urlencode({'query_term':query})
    res=urllib2.urlopen(BASE_URL+'?'+q, timeout=10)
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
        for t in m['torrents']:
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