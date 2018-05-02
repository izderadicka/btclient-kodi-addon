import urllib2
import urllib
import json
import time
import os.path

BASE_URL = "https://torrentapi.org/pubapi_v2.php"
token_file = os.path.join(os.path.dirname(__file__), "../../data/token")

class ApiError(Exception):
    pass

token = None
token_ts = 0

if (os.path.exists(token_file)):
    token_ts = os.stat(token_file).st_mtime
    with open(token_file) as f:
        token = f.read()

_EXTS = ['B', 'kB', 'MB', 'GB', 'TB']        
def human_size(sz): 
    conv = sz
    idx = 0
    while conv > 1000 and idx < len(_EXTS):
        conv = conv/ 1000.0
        idx+=1
        
    return "%0.1f %s" % (conv, _EXTS[idx])
        

def json_request(url): 
    req = urllib2.Request(url,
    headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0"})
    res = urllib2.urlopen(req,  timeout = 10)
    data =  json.load(res)
    return data
    

def search(query):
    global token, token_ts
    if token is None  or time.time() - token_ts > 15*60:
        token = json_request(BASE_URL+"?get_token=get_token&app_id=btclient").get("token")
        if not token:
            raise ApiError("Token not received")
        token_ts = time.time()
        with open(token_file, "w") as f:
            f.write(token)
            
        time.sleep(2)
            
    q=urllib.urlencode({'search_string':query})
    # &ranked=0  to get all releases not only ranked
    url = BASE_URL +  '?token=%s&app_id=btclient&mode=search&%s&min_seeders=5&sort=seeders&format=json_extended' % (token, q)       
            
    full_json_res = json_request(url)
    res= full_json_res .get('torrent_results')
    if res is None:
        raise ApiError("Got error result:%s" % full_json_res)
    
    result = []
    for r in res:
        item = {}
        sz = r['size']
        seeders = r['seeders']
        leechers = r['leechers']
        if sz > 8 * 1024 * 1024 * 1024:
            continue
        item['title'] = r['title'] + " (%s)" % human_size(r['size'])
        item['url'] = r['download']
        imdb_id = r['episode_info']['imdb']
        item['info'] = "Peers (%s/%s) IMDB id %s" % (seeders, leechers,imdb_id)
        
        
        
        result.append(item)
    
    return result
    

def resolve(url):
    return url

if __name__ == "__main__":
    print search("terminator")