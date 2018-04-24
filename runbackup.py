# coding:utf-8
# author: rogerclark
"""
use this script to run your bakcup task
"""
import os,sys
import getopt
import time
import pybackup
from infolog import logger_con

def main(argv):
    """
    the parmeters of this function
    -s, --source: the backup files' folders, use space(" ") to split
    different folder
    -d, --destination: store the zip files in this folder
    -h, --help: check help message
    :param argv:
    :return:
    """
    shortparam = 'hs:d:fi'
    longparam = ['help', 'source', 'destination', 'full', 'incr']
    fullbackup = True
    try:
        opts, args = getopt.getopt(argv, shortparam, longparam)
    except getopt.GetoptError:
        logger_con.error('wrong parameters')
        logger_con.info('runbackup.py -h [help] -s [source] -d [destination]')
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('''runbackup.py\n"
                  -h [help]: help of this script\n
                  -s [source]: the folders you want to backup,
                  for more than 2 folders, use " "(space) to seperate the folder path
                  -d [destination]: the path of backup files''')
        elif opt in ("-s", "--source"):
            folderList = arg.split(" ")
        elif opt in ("-d", "--destination"):
            backupDst = arg
        elif opt in ("-f", "--full"):
            fullbackup = True
        elif opt in ("-i", "--incr"):
            fullbackup = False

    pybackup.backupTask(srclist = folderList, dst = backupDst, fullbackup=fullbackup)

if __name__ == '__main__':
    main(sys.argv[1:])