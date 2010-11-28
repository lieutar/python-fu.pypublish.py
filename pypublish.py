#! /usr/bin/python
import sys
import re
import os
import subprocess
import string

from time            import sleep
from base64          import b64encode
from httplib         import HTTPConnection, HTTPException
from xml.dom.minidom import parseString
from telnetlib       import Telnet

from pypublish.config import Config
from pypublish.util   import *

cfg = Config()

def upload_to_fotolife(user, password, file, title,  folder=''):
    type,type_s  = get_image_type( file )
    fh      = open(file, 'rb');
    content = fh.read();
    fh.close()
    body    = '''
<?xml version="1.0"?>
<entry xmlns="http://purl.org/atom/ns#">
  <title>%s</title>
  <content mode="base64" type="%s">%s</content>
</entry>

''' % ( title, type, b64encode(content) )
    headers = {
        'Authorization': 'WSSE profile=\"UsernameToken\"',
        'X-WSSE'       : make_wsse_data(user, password),
        'Content-Type' : 'application/x.atom+xml'
        }

    con = HTTPConnection('f.hatena.ne.jp');
    con.request('POST', '/atom/post', body, headers);
    res = con.getresponse();
    if(res.status == 201):
        resbody =res.read()
        resdom  = parseString(resbody)
        links = resdom.getElementsByTagName('link')
        for link in links:
            if(link.getAttribute('rel') == 'alternate'):
                alturl = link.getAttribute('href');
                m = re.search(r'([^/]+)/([^/]+)$', alturl)
                uid = m.group(1)
                fid = m.group(2)
                return 'f:id:'+uid+':'+fid+type_s+':'+'image'
        raise HTTPException, resbody
    raise HTTPException, '%s %s' % (res.status, res.reason)



def post_to_haiku(user, title, fnotation, retry=True):
    try:
        tn = Telnet('localhost', 4242)
        _post_to_haiku(tn, user, title, fnotation)
    except:
        if not retry: raise
        launch_firefox(cfg)
        sleep(cfg.get('PROG.firefox_wait'))
        post_to_haiku(user, title, fnotation, retry = False)



def _post_to_haiku(tn, user, title, fnotation):
    tn.read_until('repl>')
    tn.write(
        "tab=gBrowser.addTab(\"http://h.hatena.ne.jp/%s\");\n"%
        (user)
        )
    cmds = '''gBrowser.selectedTab = tab;
win = tab.linkedBrowser.contentWindow;
'''
    for l in cmds.split("\n"):
        tn.read_until('repl>')
        tn.write(l.encode('utf8')+"\n")


    tn.read_until('repl>')
    tn.write("(function(num_retry){;\n")
    cmds = ('''
   if(num_retry < 1) return;
   var iter  = arguments.callee;
   var retry = function(){
       setTimeout(function(){iter(num_retry - 1);},500);
   };
   try{
     if(!win.document || !win.document.getElementsByTagName) return retry();
     var forms = win.document.getElementsByTagName('form');
     if(!forms || forms.length < 1) return retry();
     var form;
     for(var i=0,l=forms.length;i<l;i++){
        form = forms[i];
        if(!String(form.className).match(/entry-form/)) continue;
        break;
     }
     if(!form) return retry();
     var tas   = form.getElementsByTagName('textarea');
     if(!tas || tas.length < 1) return retry();
     tas[0].value = '%s';
     return undefined;
   }catch(e){
     alert(e);
   }
''' % (fnotation))
    for l in cmds.split("\n"):
        tn.read_until('....>')
        tn.write(l.encode('utf8') + "\n")
    tn.read_until('....>')
    tn.write('})(50)')



### main for cli

def cli_main(cfg):
    file = sys.argv[1]
    user     = cfg.get('haiku.user')
    password = cfg.get('haiku.password')
    title    = cfg.get('haiku.keyword') or ''
    conv     = cfg.get('PROG.imconvert')
    ident    = cfg.get('PROG.imidentify')
    suffix   = cfg.get('haiku.suffix') or '.jpg'
    maxsize  = cfg.get('haiku.maxsize') or 800
    idproc   = subprocess.Popen([ident, file], stdout=subprocess.PIPE)
    idout    = idproc.stdout.read().split(' ')
    fspaces  = len(re.findall(' ',file))
    idginfo  = idout[2 + fspaces]
    idgm     = re.match(r'(\d+)x(\d+)',idginfo)
    ow       = string.atoi(idgm.group(1))
    oh       = string.atoi(idgm.group(2))
    dw,dh    = calc_new_size(ow, oh, maxsize)
    dfile    = tmp_filename(suffix)
    convp    = subprocess.Popen([conv,
                                 file,
                                 '-scale', '%sx%s' % (dw, dh),
                                 dfile])
    convp.wait()
    fnotation = upload_to_fotolife( user, password, dfile, title )
    post_to_haiku( user, title, fnotation )
    os.unlink( dfile )




### main ###

try:
    from gimpfu          import *
    def post_to_hatena_haiku(img,drw,
                             user,
                             password,
                             title   = '',
                             maxsize = 800,
                             suffix  = '.jpg'):
        dw,dh = calc_new_size(img.width, img.height, maxsize)
        dimg = pdb.gimp_image_duplicate(img)
        dimg.flatten()
        pdb.gimp_image_scale_full(dimg, dw, dh, INTERPOLATION_CUBIC)
        dfile = tmp_filename()
        pdb.gimp_file_save(dimg, dimg.active_layer, dfile, dfile)
        pdb.gimp_image_delete(dimg)
        fnotation = upload_to_fotolife( user,  password,  dfile, title)
        post_to_haiku(user, title, fnotation)
        os.unlink(dfile)
        
    register(
        "post_to_hatena_haiku",
        "Image publishing plugin",
        "Image publishing plugin",
        "lieutar",
        "lieutar",
        "2010",
        "<Image>/File/Haiku!",
        "RGB*, GRAY*, INDEXED*",
        [
            (PF_STRING, 'user',     'username',
             cfg.get('haiku.user')     or ''),
            (PF_STRING, 'password', 'password',
             cfg.get('haiku.password') or ''),
            (PF_STRING, 'title',    'keyword', 
             cfg.get('haiku.keyword')  or ''),
            (PF_INT,    'maxsize',  'max size',
             cfg.get('haiku.maxsize')   or 800),
            (PF_STRING, 'suffix', 'suffix',
             cfg.get('haiku.suffix') or '.jpg')
            ],
        [],
        post_to_hatena_haiku)
    main()

except:
    if __name__ == '__main__':
        cli_main(cfg)
        
