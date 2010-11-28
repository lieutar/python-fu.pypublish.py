import re
import os
import yaml

class Config:

    def __init__(self, file = None):
        self.dict = {}
        if file == None:
            file = os.getenv('HOME') + os.sep + '.pypublish.yaml'
        self.config_filename = file
        self.read()

    def read(self):
        file = self.config_filename
        if not os.path.exists(file):
            return
        src = open(file).read()
        src = src.decode('utf8')
        self.dict = yaml.load(src)
        

    def save(self):
        fh = open(self.config_filename, 'w')
        yaml.dump(self.dict, fh, encoding='utf8', allow_unicode=True)
        pass

    def get(self, path):
        cur = self.dict
        for slot in path.split('.'):
            if not (slot in cur) :
                if re.match('GLOBAL', path):
                    return None
                return self.get(re.sub('^[^.]+','GLOBAL',path))
            cur = cur[slot]
        return cur

    def put(self, path, val):
        cur = self.dict
        path = path.split('.')
        last = path.pop()
        while len( path ):
            slot = path.pop(0)
            if not (slot in cur) :
                break
            cur = cur[slot]
        for slot in path:
            cur[slot] = {}
            cur = cur[slot]
        cur.last = val
