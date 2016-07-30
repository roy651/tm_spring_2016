#############################################3
# Script to load CSV records into a MySQL DB
# Records are actually coming from the XLS file
# which aggregated all the tweets but it needs
# to be saved as CSV and then placed locally
# The script is not very customized at the moment
# you need to change the hostname, db name,
# username/password and file name
###############################################3
#!/usr/bin/python
import csv
import MySQLdb
import os
# from numpy import *
# import scipy as sp
# from pandas import *
# import pandas.rpy.common as com
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

def CreateTable(_cursor, _tableName):
    try:
        print("Creating table {}: ".format(_tableName))
        _cursor.execute("CREATE TABLE `" + _tableName + "` (" +
                        "tweet_id	varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL," +
                        "tweeter_id	varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL," +
                        "tweeter_desc	varchar(512) COLLATE utf8mb4_unicode_ci," +
                        "tweet_text	varchar(512) COLLATE utf8mb4_unicode_ci," +
                        "disease	varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL," +
                        "query	varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL," +
                        "created_at	varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL," +
                        "location	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "timezone	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "tweets_per_user	varchar(50) COLLATE utf8mb4_unicode_ci," +
                        "tweeter_screen_name	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "coordinates	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "posted_by	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "talk_about	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "sarcasm	varchar(45) COLLATE utf8mb4_unicode_ci," +
                        "PRIMARY KEY (`tweet_id`))" +
                        "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")
    except MySQLdb.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

def StoreDB(_host, _user, _passwd, _db, _table, _file, _header, _delim):
    try:
        mydb = MySQLdb.connect(host=_host,
                            user=_user,
                            passwd=_passwd,
                            db=_db)
        cursor = mydb.cursor()
        CreateTable(cursor, _table)

        with open(_file) as csvfile:
            csv_data = csv.reader(csvfile, delimiter=_delim)
            cur_row = 0
            for row in csv_data:
                if cur_row > 0 or not _header:
                    row_len = min(len(row), 15)
                    columns = ['tweet_id', 'query', 'disease', 'created_at',
                                'tweeter_screen_name', 'tweet_text', 'tweeter_desc', 'location', 'timezone',
                                'tweeter_id', 'coordinates', 'tweets_per_user', 'posted_by', 'talk_about', 'sarcasm']
                    holders = ['%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                                '%s', '%s', '%s', '%s', '%s']
                    query = 'INSERT IGNORE INTO ' + _table + ' ({0}) VALUES ({1})'
                    query = query.format(','.join(columns[0:row_len]), ','.join(holders[0:row_len]))
                    cursor.execute(query, row[0:row_len])

                cur_row += 1
        mydb.commit()
        cursor.close()
    except MySQLdb.Error as e:
        print(e)
    except Exception as e:
        print("Unknown error occurred:")
        print(e)
    print "Done"

def ReadTweetsStr(_host, _user, _passwd, _db, _table, _field=None):
    try:

        db_url = URL(drivername='mysql', host=_host,
            database=_db, username=_user,
            password=_passwd)
        # eng = create_engine('mysql://root:root@localhost/text_mining')
        eng = create_engine(db_url)
        df = pd.read_sql_table(table_name=_table, con=eng, schema=_db)

        if _field != None:
            result = {}
            # int_field = _field + '_i'
            # if int_field in df:
            #     _field = int_field
            unique_values = df[_field].unique()
            for val in unique_values:
                result[val] = df[df[_field] == val].to_string(columns=['tweet_text'],
                                                            header=False,
                                                            index=False,
                                                            index_names=False)
            return result
        else:
            return df.to_string(columns=['tweet_text'], header=False, index=False, index_names=False)
            
    except MySQLdb.Error as e:
        print(e)
    except Exception as e:
        print(e)
        # print("Unknown error occurred")

def GetAllTableNames(_host, _user, _passwd, _db):
    try:
        connection = MySQLdb.connect(host=_host,
                                    user=_user,
                                    passwd=_passwd,
                                    db=_db)  # create the connection
        cursor = connection.cursor()     # get the cursor
        cursor.execute("SHOW TABLES")
        return cursor.fetchall()
    except MySQLdb.Error as e:
        print(e)
    except Exception as e:
        print(e)

def DropAllTables(_host, _user, _passwd, _db):
    try:
        connection = MySQLdb.connect(host=_host,
                                    user=_user,
                                    passwd=_passwd,
                                    db=_db)  # create the connection
        cursor = connection.cursor()     # get the cursor
        cursor.execute("SHOW TABLES")
        parts = ('DROP TABLE IF EXISTS %s;' % table for (table,) in cursor.fetchall())
        sql = 'SET FOREIGN_KEY_CHECKS = 0;\n' + '\n'.join(parts) + 'SET FOREIGN_KEY_CHECKS = 1;\n'
        connection.cursor().execute(sql)
    except MySQLdb.Error as e:
        print(e)
    except Exception as e:
        print(e)

def GetDistinctValues(_host, _user, _passwd, _db, _table, _field):
    try:

        db_url = URL(drivername='mysql', host=_host,
            database=_db, username=_user,
            password=_passwd)
        # eng = create_engine('mysql://root:root@localhost/text_mining')
        eng = create_engine(db_url)
        df = pd.read_sql_table(table_name=_table, con=eng, schema=_db)
        return df[_field].unique()

    except MySQLdb.Error as e:
        print(e)
    except Exception as e:
        print(e)
        # print("Unknown error occurred")
