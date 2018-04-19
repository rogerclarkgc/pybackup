# coding:utf-8
# author: rogerclark
"""
a script used to backup files
"""
import os, sys
import time
import shutil
import zipfile
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
            raise RuntimeError('[md5dict]:path not exits')

    def loadmd5dict(self):
        """
        load stored md5dict pickle file, return a python dict object
        """
        try:
            with open(self.dictfile, 'rb') as f:
                md5dict = pickle.load(f)
        except (FileExistsError, FileNotFoundError):
            print('[md5dict]:md5 file not found, check path:\n{}'.format(self.dictfile))
            return {}
        else:
            return md5dict

    def storemd5dict(self):
        """
        store md5 value in a dict object
        key of dict is a pair (file, filepath)
        return value is the dict used to store md5 value of files
        """
        print('[md5dict]:checking path {}...'.format(self.path))
        #flist = os.listdir(self.path)
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        newdict = {}
        print('[md5dict]:generating md5 value for {} files'.format(len(flist)))
        for root, f in flist:
            fdst = os.path.join(root, f)
            newdict[(f, fdst)] = (md5hash(fdst), fdst)
            print('[md5dict]:new file: {}     md5:{}'
            .format(newdict[(f, fdst)][1], newdict[(f, fdst)][0]))
        print('[md5dict]:writing md5dict pickle at {}'.format(self.dictfile))
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(newdict, f)
        return newdict

    def updatemd5dict(self):
        """
        update md5 dict for changing of files
        return value are two list objects, which contain changed files and Deleted
        files
        """
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        changedfile = []
        print('[md5dict]:checking md5 value for {} files'.format(len(flist)))
        with open(self.dictfile, mode='rb') as f:
            old_dict = pickle.load(f)
        oldkeys = [(i[1], i[0]) for i in old_dict.keys()]
        cplist = [(os.path.join(root, f), f) for root, f in flist]
        deletefile = [f for f in oldkeys if f not in cplist]
        for root, name in deletefile:
            print("[md5dict]:file: {} \nhas been deleted, moved or renamed"
            .format(os.path.join(root, name)))
            old_dict.pop((name, root))
        for root, f in flist:
            fdst = os.path.join(root, f)
            md5 = md5hash(fdst)
            if old_dict.get((f, fdst)):
                oldmd5 = old_dict.get((f, fdst))[0]
                oldpath = old_dict.get((f, fdst))[1]
                if oldmd5 != md5:
                    print('[md5dict]:file: {}\nhas been modified, updating md5dict'.format(fdst))
                    old_dict[(f, oldpath)] = (md5, oldpath)
                    changedfile.append((root, f))
                else:
                    print('[md5dict]:file: {}\nhas not changed, skiping'.format(fdst))
            else:
                print('[md5dict]:new file: {}\n updating md5dict'.format(fdst))
                old_dict[(f, fdst)] = (md5, fdst)
                changedfile.append((root, f))
        print('[md5dict]:updating md5dict pickle file at {}'.format(self.dictfile))
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(old_dict, f)
        return changedfile, deletefile

def fullBackup(src, dst, filename=None):
    """
    Fully backup all files in a zip file
    """
    print('[fullBackup]:preparing md5 dictionary...')
    m = md5dict(src)
    filedict = m.storemd5dict()
    if not filename:
        filename = time.strftime('%Y-%m-%d', time.localtime())+'fullbackup.zip'
    zippath = os.path.join(dst, filename)
    myzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
    print('[fullBackup]:writing zip file in :\n{}'.format(zippath))
    for f, fdst in filedict.keys():
        myzip.write(fdst, fdst.replace(src+os.sep, ''))
    myzip.close()

def incrBackup(src,dst, filename=None):
    m = md5dict(src)
    print('[incrBackup]:updating md5 dictionary...')
    chgfile, delfile = m.updatemd5dict()
    if len(chgfile) == 0:
        print('[incrBackup]:Nothing has been added, moved or modified in path:\n{}'.format(src))
    else:
        if not filename:
            filename = time.strftime('%Y-%m-%d', time.localtime()) + 'incrbackup.zip'
        zippath = os.path.join(dst, filename)
        myzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
        print('[incrBackup]:writing zip file in :\n{}'.format(zippath))
        for root, f in chgfile:
            fdst = os.path.join(root, f)
            myzip.write(fdst, fdst.replace(src+os.sep, ''))
        myzip.close()
    if len(delfile) == 0:
        print('[incrBackup]:No file has been deleted in:\n{}'.format(src))
    else:
        for fdst, fname in delfile:
            print('''[incrBackup]:file:{} has been deleted, moved or renamed\n
            path:{}'''.format(fname, fdst))
    
