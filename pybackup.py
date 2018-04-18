# coding:utf-8
# author: rogerclark
"""
a script used to backup files
"""
import os, sys
import time
import tarfile
import hashlib
import pickle

def mkdir(path):
    """
    make a folder at specific path
    """
    pathexists = os.path.exists(path)
    if pathexists:
        print('path {} has existed'.format(path))
    else:
        os.makedirs(path)
        print('path {} has created successful'.format(path))
    return not pathexists

def md5hash(filename):
    """
    calculate md5 value of a file
    """
    m = hashlib.md5()
    with open(filename, mode='rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            else:
                m.update(data)
        fhash = m.hexdigest()
    return fhash

class md5dict:
    """
    generate a dict to store every file's name and md5 value
    """
    def __init__(self, path):
        self.path = path
        self.dictfile = os.path.join(os.path.abspath('..'), 'md5dict')
        pathexists = os.path.exists(path)
        if pathexists is False:
            raise RuntimeError('path not exits')

    def storemd5dict(self):
        print('checking path {}...'.format(self.path))
        #flist = os.listdir(self.path)
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        newdict = {}
        print('generating md5 value for {} files'.format(len(flist)))
        for root, f in flist:
            fdst = os.path.join(root, f)
            newdict[(f, fdst)] = (md5hash(fdst), fdst)
            print('new file: {}     md5:{}'.format(newdict[(f, fdst)][1], newdict[(f, fdst)][0]))
        print('writing md5dict pickle at {}'.format(self.dictfile))
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(newdict, f)

    def updatemd5dict(self):
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        changedfile = []
        print('checking md5 value for {} files'.format(len(flist)))
        with open(self.dictfile, mode='rb') as f:
            old_dict = pickle.load(f)
        oldkeys = [(i[1], i[0]) for i in old_dict.keys()]
        cplist = [(os.path.join(root, f), f) for root, f in flist]
        deletefile = [f for f in oldkeys if f not in cplist]
        for root, name in deletefile:
            print("file: {} \nhas been deleted, moved or renamed"
            .format(os.path.join(root, name)))
            old_dict.pop((name, root))
        for root, f in flist:
            fdst = os.path.join(root, f)
            md5 = md5hash(fdst)
            if old_dict.get((f, fdst)):
                oldmd5 = old_dict.get((f, fdst))[0]
                oldpath = old_dict.get((f, fdst))[1]
                if oldmd5 != md5:
                    print('file: {}\nhas been modified, updating md5dict'.format(fdst))
                    old_dict[(f, oldpath)] = (md5, oldpath)
                    changedfile.append((root, f))
                else:
                    print('file: {}\nhas not changed, skiping'.format(fdst))
            else:
                print('new file: {}\n updating md5dict'.format(fdst))
                old_dict[(f, fdst)] = (md5, fdst)
                changedfile.append((root, f))
        print('updating md5dict pickle file at {}'.format(self.dictfile))
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(old_dict, f)
        return changedfile, deletefile
