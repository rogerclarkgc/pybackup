# coding:utf-8
# author: rogerclark
"""
a script used to backup files
"""
import os, sys
import time
import zipfile
import hashlib
import pickle
from infolog import logger_con, WriteLogFile, streamcol


def mkdir(path):
    """
    make a new folder at path
    :param path: path of new folder
    :return: bool value
    """
    pathexists = os.path.exists(path)
    if pathexists:
        streamcol('path {} has existed'.format(path), 'red', 'warn')
    else:
        os.makedirs(path)
        streamcol('path {} has created successful'.format(path), 'green', 'info')
    return not pathexists

def md5hash(filename):
    """
    calculate a file 's md5 hash
    :param filename: file's name
    :return: md5 hash value, str object
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
    a class to operate md5 hash for file
    """
    def __init__(self, path, dictname = None):
        """
        initiating the class
        :param path: the path of folder
        :param dictname: the name of md5file dict pickle file
        """
        self.path = path
        pathexists = os.path.exists(path)
        if pathexists is False:
            raise RuntimeError(streamcol('[md5dict]:source path not exits', 'red', 'error'))
        if not dictname:
            self.dictname = os.path.basename(path) + '.pickle'
        else:
            self.dictname = dictname
        self.dictfile = os.path.join(os.path.abspath('..'), self.dictname)


    def loadmd5dict(self):
        """
        load a md5dict pickle file
        :return: a dict object
        """
        try:
            with open(self.dictfile, 'rb') as f:
                md5dict = pickle.load(f)
        except (FileExistsError, FileNotFoundError):
            streamcol('md5 file not found, check path:\n{}'.format(self.dictfile), 'red', 'error')
            return {}
        else:
            return md5dict

    def storemd5dict(self):
        """
        store md5dict pickle file
        :return: the file 's md5 dict object
        """
        streamcol('checking path {}...'.format(self.path), 'blue', 'info')
        #flist = os.listdir(self.path)
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        newdict = {}
        streamcol('generating md5 value for {} files'.format(len(flist)), 'blue', 'info')
        for root, f in flist:
            fdst = os.path.join(root, f)
            newdict[(f, fdst)] = (md5hash(fdst), fdst)
            streamcol('new file: {}     md5:{}'.format(newdict[(f, fdst)][1], newdict[(f, fdst)][0]),
                      'green', 'info')
        streamcol('writing md5dict pickle at {}'.format(self.dictfile), 'blue', 'info')
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(newdict, f)
        return newdict

    def updatemd5dict(self):
        """
        updating md5dict
        :return: two list object, the names of changed files and deleted files
        """
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        changedfile = []
        streamcol('checking md5 value for {} files'.format(len(flist)), 'blue', 'info')
        with open(self.dictfile, mode='rb') as f:
            old_dict = pickle.load(f)
        oldkeys = [(i[1], i[0]) for i in old_dict.keys()]
        cplist = [(os.path.join(root, f), f) for root, f in flist]
        deletefile = [f for f in oldkeys if f not in cplist]
        for root, name in deletefile:
            streamcol("file: {} \nhas been deleted, moved or renamed".format(os.path.join(root, name)),
                      'red', 'info')
            old_dict.pop((name, root))
        for root, f in flist:
            fdst = os.path.join(root, f)
            md5 = md5hash(fdst)
            if old_dict.get((f, fdst)):
                oldmd5 = old_dict.get((f, fdst))[0]
                oldpath = old_dict.get((f, fdst))[1]
                if oldmd5 != md5:
                    streamcol('file: {}\nhas been modified, updating md5dict'.format(fdst),
                              'yellow', 'info')
                    old_dict[(f, oldpath)] = (md5, oldpath)
                    changedfile.append((root, f))
                else:
                    logger_con.info('file: {}\nhas not changed, skiping'.format(fdst))
            else:
                streamcol('new file: {}\n updating md5dict'.format(fdst), 'green', 'info')
                old_dict[(f, fdst)] = (md5, fdst)
                changedfile.append((root, f))
        streamcol('updating md5dict pickle file at {}'.format(self.dictfile), 'blue', 'info')
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(old_dict, f)
        return changedfile, deletefile

def fullBackup(src, dst, filename=None):
    """
    fully backup whole files under the src's directory
    :param src: the source folder you want to backup
    :param dst: the folder to store the backup zip files
    :param filename: the filename for zip files
    :return: the file dict of new files
    """
    streamcol('preparing md5 dictionary...', 'blue', 'info')
    m = md5dict(src)
    filedict = m.storemd5dict()
    if not filename:
        filename = time.strftime('%Y-%m-%d', time.localtime())+'fullbackup.zip'
    zippath = os.path.join(dst, filename)
    myzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
    streamcol('writing zip file in :\n{}'.format(zippath), 'blue', 'info')
    for f, fdst in filedict.keys():
        myzip.write(fdst, fdst.replace(src+os.sep, ''))
    myzip.close()
    return filedict

def incrBackup(src,dst, filename=None):
    """
    only backup changed files, deleted file cannot backup, only write in log
    :param src: the source folder you want to backup
    :param dst: the folder to store the backup zip files
    :param filename: the filename for zip files
    :return: the list object of changed and deleted files
    """
    m = md5dict(src)
    streamcol('updating md5 dictionary...', 'blue', 'info')
    chgfile, delfile = m.updatemd5dict()
    if len(chgfile) == 0:
        streamcol('Nothing has been added, moved or modified in path:\n{}'.format(src),
                  'blue', 'info')
    else:
        if not filename:
            filename = time.strftime('%Y-%m-%d', time.localtime()) + 'incrbackup.zip'
        zippath = os.path.join(dst, filename)
        myzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
        streamcol('writing zip file in :\n{}'.format(zippath), 'blue', 'info')
        for root, f in chgfile:
            fdst = os.path.join(root, f)
            myzip.write(fdst, fdst.replace(src+os.sep, ''))
        myzip.close()
    if len(delfile) == 0:
        streamcol('No file has been deleted in:\n{}'.format(src), 'blue', 'info')
    else:
        for fdst, fname in delfile:
            streamcol('''file:{} has been deleted, moved or renamed\npath:{}'''.format(fname, fdst),
                      'blue','info')
    return chgfile, delfile

def backupTask(srclist, dst, filenamelist=None, fullbackup=True):
    """
    wrapper for function fullBackup and incrBackup
    :param srclist:the source you want to backup, for multiple source, write in a list
    :param dst:the folder to store the backup zip files
    :param filenamelist:the backup file 's name, list object
    :param fullbackup:fullBackup or incrBackup
    :return:None
    """
    streamcol('starting backup task...', 'blue', 'info')
    for index, src in enumerate(srclist):
        if fullbackup:
            if filenamelist:
                backupFile = filenamelist[index]
            else:
                backupFile = os.path.basename(src)
                backupFile = time.strftime('%Y-%m-%d', time.localtime()) + backupFile + 'full.zip'
            streamcol('starting fullbackup for source path:{}'.format(src), 'blue', 'info')
            filelist = fullBackup(src, dst, backupFile)
            streamcol('writing log file in path:{}'.format(os.path.abspath('..')), 'blue', 'info')
            WriteLogFile(logname=os.path.basename(src), filelist=filelist, fullbackup=True)
        else:
            if filenamelist:
                backupFile = filenamelist[index]
            else:
                backupFile = os.path.basename(src)
                backupFile = time.strftime('%Y-%m-%d', time.localtime()) + backupFile + 'incr.zip'
            streamcol('starting incrbackup for source path:{}'.format(src), 'blue', 'info')
            chgfile, delfile = incrBackup(src, dst, backupFile)
            streamcol('writing log file in path:{}'.format(os.path.abspath('..')), 'blue', 'info')
            WriteLogFile(logname=os.path.basename(src), chgfile=chgfile, delfile=delfile, fullbackup=False)


