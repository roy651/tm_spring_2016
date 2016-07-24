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

try:

    mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='root',
    db='text_mining')

    cursor = mydb.cursor()

    csv_data = csv.reader(file('asthma.csv'))

    cur_row = 0
    for row in csv_data:
        # if cur_row >= start_row:
        cursor.execute('INSERT INTO `tweets` (tweet_id, query, disease, created_at, tweeter_screen_name, tweet_text, tweeter_desc, location, timezone, tweeter_id, coordinates, tweets_per_user) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', row)
        # Other processing if necessary

    cur_row += 1

    mydb.commit()
    cursor.close()

except MySQLdb.Error as e:
    print(e)

except :
    print("Unknown error occurred")



print "Done"
