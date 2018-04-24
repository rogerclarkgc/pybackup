# coding: utf-8
# author: rogerclark
"""
logging module for pybackup
"""
import time
import os, sys
import logging

# console logger
logger_con = logging.getLogger('pybackup')
logger_con.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

formatter_con = logging.Formatter("%(asctime)s-%(funcName)s-%(levelname)s: %(message)s",
datefmt = '%Y-%m-%d')
console.setFormatter(formatter_con)
logger_con.addHandler(console)

# backup file logger
logger_file = logging.getLogger('pybackup_file')
logger_file.setLevel(logging.DEBUG)

logFilepath = os.path.join(os.path.abspath('..'), 'pybackupFileLog.log')
logFilehandle = logging.FileHandler(filename=logFilepath, encoding='utf-8')
logFilehandle.setLevel(logging.DEBUG)

formatter_file = logging.Formatter('%(asctime)s-%(funcName)s: %(message)s',
datefmt = '%Y-%m-%d')
logFilehandle.setFormatter(formatter_file)
logger_file.addHandler(logFilehandle)

def streamcol(s, col):
    """
    change character's color when print on the screen
    """
    red = "\033[1;31;40m"
    green = "\033[1;32;40m"
    yellow = "\033[1;33;40m"
    blue = "\033[1;34;40m"
    end = "\033[0m"
    if col == 'red':
        out = red + s + end
    elif col == 'green':
        out = green + s + end
    elif col == 'yellow':
        out = yellow + s + end
    elif col == 'blue':
        out = blue + s + end
    return out

def WriteLogFile(logname=None, filelist=None, chgfile=None, delfile=None, fullbackup=True):
    if fullbackup:
        # type == 0, using fullBackup() method
        if not logname:
            logname = time.strftime('%Y-%m-%d-%H%M%S', time.localtime()) + '_FULL.log'
        else:
            logname = logname+time.strftime('%Y-%m-%d-%H%M%S', time.localtime())+ '_FULL.log'
        logpath = os.path.join(os.path.abspath('..'), logname)
        logger_con.info((streamcol('writing log file in path:{}'.format(logpath), 'blue')))
        logContent = ["file:{}    path:{}\n".format(key[0], key[1]) for key in filelist.keys()]
        endtext = "These files above were new files\n".format(time.strftime('%Y-%m-%d-%H%M%S', time.localtime()))
        logContent.append(endtext)
        with open(logpath, 'a', encoding='utf-8') as f:
            f.writelines(logContent)
    else:
        if not logname:
            logname = time.strftime('%Y-%m-%d-%H%M%S', time.localtime()) + '_INCR.log'
        else:
            logname = logname + time.strftime('%Y-%m-%d-%H%M%S', time.localtime()) + '_INCR.log'
        logpath = os.path.join(os.path.abspath('..'), logname)
        logger_con.info((streamcol('writing log file in path:{}'.format(logpath), 'blue')))
        chgContent = ["file:{}    path:{}\n".format(p[1], os.path.join(p[0], p[1]))
        for p in chgfile]
        chgContent.append('These files above have been modified or added\n\n\n')
        delContent = ["file:{}    path:{}\n".format(p[1], p[0]) for p in delfile]
        delContent.append('These files above have been deleted, moved or renamed\n')
        with open(logpath, 'a', encoding='utf-8') as f:
            f.writelines(chgContent+delContent)
