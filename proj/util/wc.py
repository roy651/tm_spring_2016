import sys
import MySQLdb
import os
from db_util import ReadTweetsStr
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

def strip_suffix(name):
    index = name.index('.')
    return name[:index] if index > 0 else name

def GenWordcloud(_host, _user, _passwd, _db, _table, _name):
    grdevices = importr('grDevices')
    ro.r('library(wordcloud)')
    ro.r('library(tm)')
    all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table)
    grdevices.png(file=strip_suffix(_name)+".png", width=512, height=512)
    #  ro.r('wordcloud("' + all_text + '", colors=brewer.pal(6,"Dark2"),random.order=FALSE)')
    ro.r('wordcloud("' + all_text + '",' +
         'max.words=100, min.freq=10,' +
         'scale=c(5,1), rot.per=0.35,' +
         'colors=brewer.pal(6,"Dark2"),' +
         'random.order=FALSE)')
    grdevices.dev_off()
