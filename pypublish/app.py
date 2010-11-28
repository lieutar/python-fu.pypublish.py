from .util import *
from .config import Config
import subprocess


class App:
    def __init__():
        self.cfg  = Config()

    def im_image_get_size(self, file):
        cfg      = self.cfg
        ident    = cfg.get('PROG.imidentify')
        maxsize  = cfg.get('haiku.maxsize') or 800
        idproc   = subprocess.Popen([ident, file], stdout=subprocess.PIPE)
        idout    = idproc.stdout.read().split(' ')
        fspaces  = len(re.findall(' ',file))
        idginfo  = idout[2 + fspaces]
        idgm     = re.match(r'(\d+)x(\d+)',idginfo)
        ow       = string.atoi(idgm.group(1))
        oh       = string.atoi(idgm.group(2))
        return calc_new_size(ow, oh, maxsize)

    def im_image_resize(self, file):
        dw,dh    = self.im_image_get_size(file)
        dfile    = tmp_filename(suffix)
        convp    = subprocess.Popen([conv,
                                     file,
                                     '-scale', '%sx%s' % (dw, dh),
                                     dfile])
        convp.wait()
        return dfile

    def fu_image_resize(self, img):
        dw,dh = calc_new_size(img.width, img.height, maxsize)
        dimg = pdb.gimp_image_duplicate(img)
        dimg.flatten()
        pdb.gimp_image_scale_full(dimg, dw, dh, INTERPOLATION_CUBIC)
        dfile = tmp_filename()
        pdb.gimp_file_save(dimg, dimg.active_layer, dfile, dfile)
        pdb.gimp_image_delete(dimg)
        pass


    def fu_main():
        def post_to_hatena_haiku(img,drw,
                                 title   = '',
                                 maxsize = 800,
                                 suffix  = '.jpg'):
            dfile = self.fu_image_resize(img)
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

        pass

    def cli_main():
        pass

    def main(self):
        try:
            from gimpfu import *
            self.fu_main():
        except:
            self.cli_main():


