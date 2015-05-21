Contains search plugins for various sources.

each plugin is module with two mandatory methods:

def search(query)

Returns list of dictionary objects 
d['title'] - title of video file
d['url'] - url of video file
d['img'] - url of thumbnail image
d['size'] - file size (as text)
d['length'] - time duration
d['info'] 

def resolve(url)

Resolves url from search to url that can be used by BTClient - e.g.
http link to video file
http link to torrent file
magnet link
http link to known file sharing server (BTClient must have plugin for it)