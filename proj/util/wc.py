import sys
import MySQLdb
import os
from db_util import ReadTweetsStr
from db_util import GetDistinctValues
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

def strip_suffix(name):
    index = name.index('.') if '.' in name else 0
    return name[:index] if index > 0 else name

def GenWordcloud(_host, _user, _passwd, _db, _table, _name, _group):
    ro.r('library(wordcloud)')
    ro.r('library(tm)')
    if _group in ['talk_about', 'sarcasm', 'posted_by']:
        all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table, _group)
        for text_key, text_value in all_text.items():
            run_wordcloud(text_value, _name, _group, text_key)
    else:
        all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table)
        run_wordcloud(all_text, _name)

def run_wordcloud(_all_text, _name, _group=None, _value=None):
    new_suffix = '_' + _group + '_' + _value if _group is not None else ''
    grdevices = importr('grDevices')
    wc = importr('wordcloud')
    grdevices.png(file=strip_suffix(_name)+new_suffix+".png", width=512, height=512)
    wc.wordcloud(_all_text, max_words=100, min_freq=6, rot_per=0.35,
        scale=ro.r('c(5,0.8)'), colors=ro.r('brewer.pal(6,"Dark2")'), random_order=False)
    grdevices.dev_off()

def GenWordcloudRaw(_words, _freqs, _name, _group=None, _value=None):
    new_suffix = '_' + _group + '_' + _value if _group is not None else ''
    ro.r('library(wordcloud)')
    ro.r('library(tm)')
    grdevices = importr('grDevices')
    wc = importr('wordcloud')
    grdevices.png(file=strip_suffix(_name)+new_suffix+".png", width=512, height=512)
    wc.wordcloud(words=ro.StrVector(_words), freq=ro.FloatVector(_freqs), rot_per=0.35,
        scale=ro.r('c(5,0.8)'), colors=ro.r('brewer.pal(3,"Greens")'), random_order=False)
    grdevices.dev_off()
