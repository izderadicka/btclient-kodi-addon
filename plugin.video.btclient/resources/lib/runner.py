'''
Created on May 14, 2015

@author: ivan
'''

import os.path
import subprocess
from threading import Thread, Event
import sys
import re
import signal
import tempfile
import urllib2
import xbmc
import json


class Client(object):
    def __init__(self, download_dir, log_file=None, port=5002, delete_on_finish=False, clear_older=0,
                 bt_download_limit=0, bt_upload_limit=0):
        pyfile=self._find_exe()
        if not pyfile:
            raise Exception('btclient.py not found')
        self.params=['python', pyfile, '--stream', '--quiet', '-d', download_dir]
        if log_file:
            self.params.extend(['--debug-log', log_file])
        if port:
            self.params.extend(['--port', str(port)])
        if delete_on_finish:
            self.params.append('--delete-on-finish')   
        if clear_older:
            self.params.extend(['--clear-older', str(clear_older)]) 
        if bt_download_limit:
            self.params.extend(['--bt-download-limit', str(bt_download_limit)])
        if bt_upload_limit:
            self.params.extend(['--bt-upload-limit', str(bt_upload_limit)])
        self._p=None
        self._wait_ready=Event()
        self.link=None
        
        self.status_url="http://localhost:%d/status" % port
        
    @property    
    def status(self):
        try:
            resp=urllib2.urlopen(self.status_url,  timeout=5)
            status= json.load(resp)
            mb=float(1024*1024)
            kb=float(1024)
            msg="""{status} - Downloaded:  {progress:.2%} {downloaded:.0f}MB/{total_size:.0f}MB
Down. Rate {byte_rate:.1f}kB/s (need {desired_rate:.1f}kB/s)""".format(
            status=status['state'],
            progress=status['progress'], 
            downloaded=(status['downloaded'] or 0)/mb,
            total_size=(status['total_size'] or 0)/mb, 
            byte_rate=(status['download_rate'] or 0)/kb,
            desired_rate=(status['desired_rate'] or 0)/kb)
            return msg
        except Exception,e:
            xbmc.log('Error while getting status: %s'%e, xbmc.LOGERROR)
            return ''
            
        
    LINK_RE=re.compile('^Serving file on (http://.*)$', re.IGNORECASE| re.UNICODE)
    def _read_stdout(self):
        while True:
            l=self._p.stdout.readline()
            if not l:
                break
            link=Client.LINK_RE.match(unicode(l,'utf8'))
            if link:
                self.link=link.group(1)
                self._wait_ready.set()
        #process ended
        self._wait_ready.set()
    
    
    def poll_ready(self, interval):    
        return self._wait_ready.wait(interval)
    
    def wait_ready(self):
        if not self._wait_ready.wait(120):
            if self._p:
                try:
                    self._p.kill()
                except:
                    pass
            raise Exception('Client is not ready in given deadline')
        else:
            if self._p.poll() is not None:
                raise Exception('Client ended early')
        
    def start(self, url):   
        self._p=subprocess.Popen(self.params+[url], stdout=subprocess.PIPE, shell=False) 
        t=Thread(name='reader', target=self._read_stdout)
        t.daemon=True
        t.start()
        
    def stop(self):
        
        if self._p:
            try:
                self._p.send_signal(signal.SIGTERM)
            except:
                pass
    close=stop
            
    def wait_finish(self):
        if not self._p:
            return
        return self._p.wait()
    
    @property
    def pid(self):
        if self._p:
            return self._p.pid
        
    def _find_exe(self):
        for p in os.environ.get('PATH', '').split(':'):
            exe=os.path.join(p, 'btclient')
            if os.access(exe, os.X_OK):
                rp=os.path.realpath(exe)
                pyfile= os.path.join(os.path.split(rp)[0], 'btclient.py')
                if os.access(pyfile, os.R_OK):
                    return pyfile
 
if __name__=='__main__': 
    link=sys.argv[1]
    td=tempfile.mkdtemp()
    c=Client(td,os.path.join(td,'btclient.log'))  
    print 'Starting client'
    c.start(link)   
    print 'Client running with pid %d' % c.pid
    c.wait_ready()   
    print "Got link %s" % c.link
    ret=c.wait_finish()   
    print "Finished with code %d"   % ret