import pandas as pd
import sys
import MySQLdb
import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

try:

    # mydb = MySQLdb.connect(host='localhost',
    # user='root',
    # passwd='root',
    # db='text_mining')

    # db_url = URL(drivername='mysql', host='localhost',
    #     database='text_mining', user='root',
    #     passwd='root')
    eng = create_engine('mysql://root:root@localhost/text_mining')

    df = pd.read_sql_table(table_name='tweets', con=eng, schema='text_mining')
    df.drop_duplicates(['tweet_text'], inplace=True)
    df.to_sql('tweets_deduped', eng, 'mysql', 'text_mining', if_exists='replace')
    print "Success"

except MySQLdb.Error as e:
    print(e)

except Exception as e:
    print(e)
    # print("Unknown error occurred")



print "Done"
