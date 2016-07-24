import sys
import MySQLdb
import os
from db_util import ReadTweetsStr
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

def GenWordcloud(_host, _user, _passwd, _db, _table):
    ro.r('library(wordcloud)')
    ro.r('library(tm)')
    all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table)
    ro.r('wordcloud("' + all_text + '", colors=brewer.pal(6,"Dark2"),random.order=FALSE)')
