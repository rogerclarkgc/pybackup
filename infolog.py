# coding: utf-8
# author: rogerclark
"""
logging module for pybackup
"""
import time
import os
import sys
import platform
import ctypes
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

def streamcol_unix(s, col, infotype):
    """
    change color of characters on console, only use in ANSI standard
    console
    :param s: string on screen
    :param col: color of screen, can use 'red', 'green', 'yellow', 'blue'
    :param infotype: type of info , can use 'info', 'warn', 'error'
    :return: None
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
    text_console = "logger_con." + infotype + "(out)"
    eval(text_console)

def streamcol_win(s, col, infotype):
    """
    change the color of characters on win-like console
    :param s: string on screen
    :param col: color of characters, 'black', 'white', 'green', 'red', 'yellow', 'blue'
    :param infotype: type of info, can use 'info', 'warn', 'error'
    :return: None
    """
    std_output_handle = -11
    black = 0x00
    white = 0x0f
    green = 0x0a
    red = 0x0c
    yellow = 0x0e
    blue = 0x0b
    screenHandle = ctypes.windll.kernel32.GetStdHandle(std_output_handle)
    if col == 'black':
        ctypes.windll.kernel32.SetConsoleTextAttribute(screenHandle, black)
    elif col == 'green':
        ctypes.windll.kernel32.SetConsoleTextAttribute(screenHandle, green)
    elif col == 'red':
        ctypes.windll.kernel32.SetConsoleTextAttribute(screenHandle, red)
    elif col == 'yellow':
        ctypes.windll.kernel32.SetConsoleTextAttribute(screenHandle, yellow)
    elif col == 'blue':
        ctypes.windll.kernel32.SetConsoleTextAttribute(screenHandle, blue)
    text_console = "logger_con." + infotype + "(s)"
    eval(text_console)
    ctypes.windll.kernel32.SetConsoleTextAttribute(screenHandle, 0x07)

def streamcol(s, col, infotype):
    """
    wrapper of streamcol
    :param s: string on sreen
    :param col: color of characters
    :param infotype: type of info for logger.con object
    :return: None
    """
    if platform.system() == "Windows":
        streamcol_win(s, col, infotype)
    else:
        streamcol_unix(s, col, infotype)


def WriteLogFile(logname=None, filelist=None, chgfile=None, delfile=None, fullbackup=True):
    """
    Write a log file in disk
    :param logname: the name of log file, if None, the name will look like time + _FULL.log/_INCR.LOG
    :param filelist: the new file list of backup
    :param chgfile: the files which have changed
    :param delfile: the files which have deleted
    :param fullbackup: fullbackup or incrbackup
    :return: None
    """
    if fullbackup:
        # type == 0, using fullBackup() method
        if not logname:
            logname = time.strftime('%Y-%m-%d-%H%M%S', time.localtime()) + '_FULL.log'
        else:
            logname = logname+time.strftime('%Y-%m-%d-%H%M%S', time.localtime())+ '_FULL.log'
        logpath = os.path.join(os.path.abspath('..'), logname)
        streamcol('writing log file in path:{}'.format(logpath), 'blue', 'info')
        logContent = ["file:{}    path:{}\n".format(key[0], key[1]) for key in filelist.keys()]
        endtext = "These were {} files above were new files\n".format(len(logContent))
        logContent.append(endtext)
        with open(logpath, 'a', encoding='utf-8') as f:
            f.writelines(logContent)
    else:
        if not logname:
            logname = time.strftime('%Y-%m-%d-%H%M%S', time.localtime()) + '_INCR.log'
        else:
            logname = logname + time.strftime('%Y-%m-%d-%H%M%S', time.localtime()) + '_INCR.log'
        logpath = os.path.join(os.path.abspath('..'), logname)
        streamcol('writing log file in path:{}'.format(logpath), 'blue', 'info')
        chgContent = ["file:{}    path:{}\n".format(p[1], os.path.join(p[0], p[1]))
        for p in chgfile]
        chgContent.append('There are {} files above have been modified or added\n\n\n'.format(len(chgContent)))
        delContent = ["file:{}    path:{}\n".format(p[1], p[0]) for p in delfile]
        delContent.append('There are {} files above have been deleted, moved or renamed\n'.format(len(delContent)))
        with open(logpath, 'a', encoding='utf-8') as f:
            f.writelines(chgContent+delContent)



if __name__ == '__main__':
    testtxt = "haha"
    streamcol(testtxt, 'green', 'info')
