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
    make a folder at specific path
    """
    pathexists = os.path.exists(path)
    if pathexists:
        logger_con.warn(streamcol('path {} has existed'.format(path), 'red'))
    else:
        os.makedirs(path)
        logger_con.info(streamcol('path {} has created successful'.format(path), 'green'))
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
    def __init__(self, path, dictname = None):
        self.path = path
        pathexists = os.path.exists(path)
        if pathexists is False:
            raise RuntimeError(streamcol('[md5dict]:source path not exits', 'red'))
        if not dictname:
            self.dictname = os.path.basename(path) + '.pickle'
        else:
            self.dictname = dictname
        self.dictfile = os.path.join(os.path.abspath('..'), self.dictname)


    def loadmd5dict(self):
        """
        load stored md5dict pickle file, return a python dict object
        """
        try:
            with open(self.dictfile, 'rb') as f:
                md5dict = pickle.load(f)
        except (FileExistsError, FileNotFoundError):
            logger_con.error(streamcol('md5 file not found, check path:\n{}'
            .format(self.dictfile), 'red'))
            return {}
        else:
            return md5dict

    def storemd5dict(self):
        """
        store md5 value in a dict object
        key of dict is a pair (file, filepath)
        return value is the dict used to store md5 value of files
        """
        logger_con.info(streamcol('checking path {}...'.format(self.path), 'blue'))
        #flist = os.listdir(self.path)
        flist = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                flist.append((root, name))
        newdict = {}
        logger_con.info(streamcol('generating md5 value for {} files'
        .format(len(flist)), 'blue'))
        for root, f in flist:
            fdst = os.path.join(root, f)
            newdict[(f, fdst)] = (md5hash(fdst), fdst)
            logger_con.info(streamcol('new file: {}     md5:{}'
            .format(newdict[(f, fdst)][1], newdict[(f, fdst)][0]), 'green'))
        logger_con.info(streamcol('writing md5dict pickle at {}'
        .format(self.dictfile), 'blue'))
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
        logger_con.info(streamcol('checking md5 value for {} files'
        .format(len(flist)), 'blue'))
        with open(self.dictfile, mode='rb') as f:
            old_dict = pickle.load(f)
        oldkeys = [(i[1], i[0]) for i in old_dict.keys()]
        cplist = [(os.path.join(root, f), f) for root, f in flist]
        deletefile = [f for f in oldkeys if f not in cplist]
        for root, name in deletefile:
            logger_con.info(streamcol("file: {} \nhas been deleted, moved or renamed"
            .format(os.path.join(root, name)), 'red'))
            old_dict.pop((name, root))
        for root, f in flist:
            fdst = os.path.join(root, f)
            md5 = md5hash(fdst)
            if old_dict.get((f, fdst)):
                oldmd5 = old_dict.get((f, fdst))[0]
                oldpath = old_dict.get((f, fdst))[1]
                if oldmd5 != md5:
                    logger_con.info(streamcol('file: {}\nhas been modified, updating md5dict'
                    .format(fdst), 'yellow'))
                    old_dict[(f, oldpath)] = (md5, oldpath)
                    changedfile.append((root, f))
                else:
                    logger_con.info('file: {}\nhas not changed, skiping'.format(fdst))
            else:
                logger_con.info(streamcol('new file: {}\n updating md5dict'
                .format(fdst), 'green'))
                old_dict[(f, fdst)] = (md5, fdst)
                changedfile.append((root, f))
        logger_con.info(streamcol('updating md5dict pickle file at {}'
        .format(self.dictfile), 'blue'))
        with open(self.dictfile, mode = 'wb+') as f:
            pickle.dump(old_dict, f)
        return changedfile, deletefile

def fullBackup(src, dst, filename=None):
    """
    Fully backup all files in a zip file
    """
    logger_con.info(streamcol('preparing md5 dictionary...', 'blue'))
    m = md5dict(src)
    filedict = m.storemd5dict()
    if not filename:
        filename = time.strftime('%Y-%m-%d', time.localtime())+'fullbackup.zip'
    zippath = os.path.join(dst, filename)
    myzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
    logger_con.info(streamcol('writing zip file in :\n{}'.format(zippath), 'blue'))
    for f, fdst in filedict.keys():
        myzip.write(fdst, fdst.replace(src+os.sep, ''))
    myzip.close()
    return filedict

def incrBackup(src,dst, filename=None):
    """
    only backup changed files, including modified, changed path and added
    the deleted file cannot be recovered, only write in backup log
    """
    m = md5dict(src)
    logger_con.info(streamcol('updating md5 dictionary...', 'blue'))
    chgfile, delfile = m.updatemd5dict()
    if len(chgfile) == 0:
        logger_con.info(streamcol('Nothing has been added, moved or modified in path:\n{}'
        .format(src), 'blue'))
    else:
        if not filename:
            filename = time.strftime('%Y-%m-%d', time.localtime()) + 'incrbackup.zip'
        zippath = os.path.join(dst, filename)
        myzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
        logger_con.info(streamcol('writing zip file in :\n{}'
        .format(zippath), 'blue'))
        for root, f in chgfile:
            fdst = os.path.join(root, f)
            myzip.write(fdst, fdst.replace(src+os.sep, ''))
        myzip.close()
    if len(delfile) == 0:
        logger_con.info(streamcol('No file has been deleted in:\n{}'
        .format(src), 'blue'))
    else:
        for fdst, fname in delfile:
            logger_con.info(streamcol('''file:{} has been deleted, moved or renamed\n
            path:{}'''.format(fname, fdst), 'blue'))
    return chgfile, delfile

def backupTask(srclist, dst, filenamelist=None, fullbackup=True):
    """
    backup multiply path in a specific path
    """
    # FIXME:need to change the md5file's name to fit multiply path's requirement
    logger_con.info(streamcol('starting backup task...', 'blue'))
    for index, src in enumerate(srclist):
        if fullbackup:
            if filenamelist:
                backupFile = filenamelist[index]
            else:
                backupFile = os.path.basename(src)
                backupFile = time.strftime('%Y-%m-%d', time.localtime()) + backupFile + 'full.zip'
            logger_con.info(streamcol('starting fullbackup for source path:{}'
            .format(src), 'blue'))
            filelist = fullBackup(src, dst, backupFile)
            logger_con.info(streamcol('writing log file in path:{}'.format(os.path.abspath('..')), 'blue'))
            WriteLogFile(logname=os.path.basename(src), filelist=filelist, fullbackup=True)
        else:
            if filenamelist:
                backupFile = filenamelist[index]
            else:
                backupFile = os.path.basename(src)
                backupFile = time.strftime('%Y-%m-%d', time.localtime()) + backupFile + 'incr.zip'
            logger_con.info(streamcol('starting incrbackup for source path:{}'
            .format(src), 'blue'))
            chgfile, delfile = incrBackup(src, dst, backupFile)
            logger_con.info(streamcol('writing log file in path:{}'.format(os.path.abspath('..')), 'blue'))
            WriteLogFile(logname=os.path.basename(src), chgfile=chgfile, delfile=delfile, fullbackup=False)


