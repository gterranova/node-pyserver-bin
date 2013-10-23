import inspect
import logging
import imp
import sys
import os

class ImportEx(object):
    def __init__(self, *args):
        self.alternative_paths = args
        self.module_info = None
        self.altname = None
        self.search_paths = []

    def update_search_paths(self):
        newpaths = []
        for p in list([os.path.dirname(inspect.stack()[2][1]), os.getcwd()]+sys.path[1:]):
            fullpath = os.path.realpath(p)
            for altp in self.alternative_paths:
                if fullpath.startswith(altp):
                    newpaths.extend([os.path.join(basep, fullpath[len(altp)+1:]) for basep in self.alternative_paths])
        self.search_paths = list(set(newpaths))
        ##print "Search paths\n%s" % '\n'.join(self.search_paths)

    def is_in_path(self, s):
        s = s.replace('.', os.sep)
        s = s.replace('/', os.sep)
        parts = os.path.join(os.getcwd(),s).split(os.sep)
        while len(parts)> 0:
            fullpath = os.sep.join(parts)
            ##print "  in %s" % fullpath
            for altp in self.alternative_paths:
                if fullpath.startswith(altp):
                    return fullpath[len(altp)+1:].split(os.sep)
            parts.pop()
                
        return None
            
    def find_module(self, fullname, path=None):
        self.update_search_paths()
        """
        print "Looking for module %s" % fullname
        
        tail = self.is_in_path(fullname)
        if tail != None:
            
            print "Module %s in path (tail %r)" % (fullname, tail)
            for p in self.alternative_paths:
                altname = os.path.join(os.path.basename(p),*tail).replace(os.sep, '.')
                print "testing %s" % altname
                try:
                    self.module_info = imp.find_module(altname, path)
                    self.altname = altname
                    return self
                except:
                    continue
            
            for p in self.alternative_paths:
                parts = tail
                searchparts = [p]
                while len(parts)>0:
                    altname = '.'.join(parts)
                    newpath = os.path.join(*searchparts)
                    print "testing2 %s in %s" % ( altname, newpath)
                    try:
                        self.module_info = imp.find_module(altname, [newpath])
                        self.altname = altname
                        return self
                    except:
                        pass
                    searchparts.append(parts[0])
                    parts = parts[1:]
            """
        for p in self.search_paths:
            altname = fullname
            ##print "testing3 %s in %s" % ( altname, p)
            try:
                self.module_info = imp.find_module(altname, [p])
                self.altname = altname
                return self
            except:
                pass
                
        return None
    
    def load_module(self, name):
        module = imp.load_module(self.altname, *self.module_info)
        sys.modules[name] = module
        return module

original_meta_path = sys.meta_path[:]

def mountDirs(*args):
    sys.meta_path = [ImportEx(*args)]

def restoreDefaults():
    sys.meta_path = orignal_meta_path
    
