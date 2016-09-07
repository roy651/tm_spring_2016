import pandas as pd
import sys
import MySQLdb
import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import numpy as np
import re
import hashlib
from nltk.corpus import stopwords
from happyfuntokenizer import Tokenizer

r = re.compile('^\s*(NULL)*\s*$')
stop = stopwords.words('english') + ['https://t.co', 'http://t.co', 'https', ':/', 'co', '/', '&', 'amp', ';'] #, '.', '*', ',', '-']
tok = Tokenizer(preserve_case=False)

def int_overflow(val):
  if not -sys.maxint-1 <= val <= sys.maxint:
    val = (val + (sys.maxint + 1)) % (2 * (sys.maxint + 1)) - sys.maxint - 1
  return val

def GenIntFromStr(x):
        return int_overflow(int(hashlib.md5(x).hexdigest(), 16))

def SelectValue(x, y, r):
    if (r.match(x)):
        return GenIntFromStr(y)
    else:
        return int(x)

def SarcasmInt(x):
    return {
        'Sarcasm': 1,
        'sarcasm': 1,
        'no': 0,
        'No': 0,
        '': 0,
        'None': 0,
        None: 0,
    }.get(x, 2)

def PostedByInt(x):
    return {
        'Individual': 1,
        'individual': 1,
        'organization': 2,
        'organizational': 2,
        'none': 3,
        'None': 3,
        None: 3,
    }.get(x, 4)

def TalkAboutInt(x):
    return {
        'celeb': 1,
        'Celebrity': 1,
        'celeberity, etc.': 1,
        'dont_know': 2,
        'don\'t know': 2,
        'family': 3,
        'himself': 4,
        'knows': 5,
        'somebody known personally': 5,
        'none': 6,
        'None': 6,
        None: 6,
        'subject': 7,
    }.get(x, 8)

def SarcasmStr(x):
    return {
        1: 'Sarcasm',
        0: 'None',
        2: 'NA',
    }.get(x, 'NA')

def PostedByStr(x):
    return {
        1: 'Individual',
        2: 'Organization',
        3: 'None',
        4: 'NA',
    }.get(x, 'NA')

def TalkAboutStr(x):
    return {
        1: 'Celeb',
        2: 'DontKnow',
        3: 'Family',
        4: 'Himself',
        5: 'Knows',
        6: 'None',
        7: 'Subject',
        8: 'NA',
    }.get(x, 'NA')

def ClearStopwords(sentence):
    return " ".join([i for i in tok.tokenize(sentence) if i not in stop])

def clearDisease(x, y):
    return re.sub(y,"",x)
    
def DedupRecords(_host, _user, _passwd, _db, _table):
    # try:

        db_url = URL(drivername='mysql', host=_host,
            database=_db, username=_user,
            password=_passwd)
        # eng = create_engine('mysql://root:root@localhost/text_mining')
        eng = create_engine(db_url)
        deduped_table = _table + '_de'

        df = pd.read_sql_table(table_name=_table, con=eng, schema=_db)
        df.drop_duplicates(['tweet_text'], inplace=True)

        df['tweeter_id'] = df[['tweeter_id','tweeter_screen_name']].apply(lambda x: SelectValue(x[0], x[1], r), axis=1)
        df[['tweeter_id', 'tweet_id']] = df[['tweeter_id', 'tweet_id']].astype(int)
        df['sarcasm_i'] = df['sarcasm'].apply(SarcasmInt)
        df['sarcasm'] = df['sarcasm_i'].apply(SarcasmStr)
        df['talk_about_i'] = df['talk_about'].apply(TalkAboutInt)
        df['talk_about'] = df['talk_about_i'].apply(TalkAboutStr)
        df['posted_by_i'] = df['posted_by'].apply(PostedByInt)
        df['posted_by'] = df['posted_by_i'].apply(PostedByStr)
        df['tweet_text'] = df['tweet_text'].apply(ClearStopwords)
        df['tweet_text'] = df['tweet_text'].str.replace(r"(^|\s)[0-9]+( |$)", " ")
        df['tweet_text'] = df[['tweet_text','disease']].apply(lambda x: clearDisease(x[0],x[1].lower()), axis=1) 
        df.drop_duplicates(['tweet_text'], inplace=True)
        df.to_sql(deduped_table, eng, 'mysql', _db, if_exists='replace')
        print "Success"

    # except MySQLdb.Error as e:
    #     print(e)
    #     raise e
    #
    # except Exception as e:
    #     print(e)
    #     raise e
        # print("Unknown error occurred")

        return deduped_table
