import os
import re
import subprocess
from hashlib         import sha1
from datetime        import datetime
from base64          import b64encode
from random          import random

__all__ = ['make_wsse_data',
           'launch_firefox',
           'get_image_type',
           'calc_new_size',
           'tmp_filename']

def make_wsse_data(user, password):
    nh = sha1()
    dh = sha1()
    nh.update("%s" % random())
    created = re.compile(r'\.[0-9]+$'
                         ).sub('',datetime.today().isoformat()) + 'Z'
    nonce   = nh.digest()
    dh.update(nonce + created + password)
    digest  = dh.digest()
    return ( 'UsernameToken'
             ' Username="%s",'
             ' PasswordDigest="%s",'
             ' Nonce="%s",'
             ' Created="%s"' % (user, 
                                b64encode(digest), 
                                b64encode(nonce),
                                created ))

def launch_firefox(cfg):
    firefox_bin = cfg.get('PROG.firefox')
    subprocess.Popen([firefox_bin])


def get_image_type(file):
    pat = re.compile(r"\.(gif|png|jpe?g)$", re.IGNORECASE)
    m = pat.search(file)
    if m:
        suffix = (m.group(1)).lower()
        if suffix == 'gif' : return  "image/gif",'g'
        if suffix == 'png' : return  "image/png",'p'
        return "image/jpeg",'j'
    raise ValueError



def calc_new_size(ow, oh, maxsize = 800):
    dw  = ow
    dh  = oh
    if ow > oh:
        if ow > maxsize:
            dw = maxsize
            dh = dw * oh / ow
    else:
        if oh > maxsize:
            dh = maxsize
            dw = dh * ow / oh
    return dw, dh

def tmp_filename(suffix = '.jpg'):
    tmp = os.getenv('TMP') or '/tmp'
    return tmp + os.sep + ('%s%s' % (random(), suffix))


