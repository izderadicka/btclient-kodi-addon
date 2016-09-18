

import subprocess
import tempfile
import os, os.path
import logging
import sys
import threading

PHANTOM='phantomjs' 
local_ps = os.path.join(os.path.dirname(__file__), '../data/phantomjs')
if os.access(local_ps, os.R_OK|os.X_OK):
    PHANTOM = local_ps





class PhantomError(Exception):
    pass
class JSEngine(object):
    def __init__(self, script, timeout=120):
        self.timeout=timeout
        self.script = script
        
    def eval(self, url):
        try:
            #p=subprocess.Popen()
            proc=subprocess.Popen([PHANTOM, '--load-images=no', '--disk-cache=true', '--max-disk-cache-size=10000', 
                                   self.script, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            to=threading.Timer(self.timeout, lambda: proc.kill())
            to.start()
            stdout, stderr=proc.communicate()
            to.cancel()
            if proc.returncode == 0:
                res=unicode(stdout, 'UTF8').strip()
                return res
            else:
                logging.error('Phantom error %d\nstdout: %s\nstderr:%s ', proc.returncode, stdout, stderr)
            
           
        except Exception as e:
            logging.exception('Error parsing JS')
       
            
            
if __name__ == '__main__':
    script = os.path.join(os.path.dirname(__file__), '../data/ulozto.js')
    engine= JSEngine(script, 10)
    print engine.eval(sys.argv[1])
            
        
        