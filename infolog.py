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

formatter_con = logging.Formatter('%(asctime)s-%(funcName)s-%(levelname)s: %(message)s',
datefmt = '%Y-%m-%d')
console.setFormatter(formatter_con)
logger_con.addHandler(console)

# backup file logger
logger_file = logging.getLogger('pybackup')
logger_file.setLevel(logging.DEBUG)

logFilepath = os.path.join(os.path.abspath('..'), 'pybackupFileLog.log')
logFilehandle = logging.FileHandler(filename=logFilepath, encoding='utf-8')
logFilehandle.setLevel(logging.DEBUG)

formatter_file = logging.Formatter('%(asctime)s-%(funcName)s: %(message)s',
datefmt = '%Y-%m-%d')
logFilehandle.setFormatter(formatter_file)
logger_file.addHandler(logFilehandle)
