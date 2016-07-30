import sys
import MySQLdb
import os
from db_util import ReadTweetsStr
from db_util import GetDistinctValues
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

def strip_suffix(name):
    index = name.index('.')
    return name[:index] if index > 0 else name

def GenWordcloud(_host, _user, _passwd, _db, _table, _name, _group):
    ro.r('library(wordcloud)')
    ro.r('library(tm)')
    if _group in ['talk_about', 'sarcasm', 'posted_by']:
        all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table, _group)
        for text_key, text_value in all_text.items():
            run_word_cloud(text_value, _name, _group, text_key)
    else:
        all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table)
        run_word_cloud(all_text, _name)

def run_word_cloud(_all_text, _name, _group=None, _value=None):
    new_suffix = '_' + _group + '_' + _value if _group is not None else ''
    grdevices = importr('grDevices')
    grdevices.png(file=strip_suffix(_name)+new_suffix+".png", width=512, height=512)
    ro.r('wordcloud("' + _all_text + '",' +
         'max.words=100, min.freq=6,' +
         'scale=c(5,0.8), rot.per=0.35,' +
         'colors=brewer.pal(6,"Dark2"),' +
         'random.order=FALSE)')
    grdevices.dev_off()
