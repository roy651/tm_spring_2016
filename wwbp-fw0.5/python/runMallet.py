# set up logging so we see what's going on
import logging
import os
import MySQLdb
from gensim import corpora, models, utils
logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

def iter_rows(table_name):
    """Iterate over all the table rows, yielding one row at a time."""
    try:
        mydb = MySQLdb.connect(host='localhost',
        user='root',
        passwd='root',
        db='text_mining')

        cursor = mydb.cursor()
        # Prepare SQL query
        sql = "SELECT tweet_text FROM %s" % (table_name)

        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            document = row[0]
            # parse document into a list of utf8 tokens
            yield utils.simple_preprocess(document)

        cursor.close()
        mydb.close()

    except MySQLdb.Error as e:
        print(e)

    except :
        print("Unknown error occurred")


class InitCorpus(object):
    def __init__(self, table_name):
        self.table_name = table_name
        self.dictionary = corpora.Dictionary(iter_rows(table_name))
        stoplist = set('for a of the and to in is my you i with for an in that this it have me just when be it\'s cant im amp at on 3 http https & * ; ... # | - ! ? / , : rt . https://t.co '.split())
        stop_ids = [self.dictionary.token2id[stopword] for stopword in stoplist if stopword in self.dictionary.token2id]
        self.dictionary.filter_tokens(stop_ids)
        self.dictionary.filter_extremes()  # remove stopwords etc

    def __iter__(self):
        for tokens in iter_rows(self.table_name):
            yield self.dictionary.doc2bow(tokens)

# set up the streamed corpus
corpus = InitCorpus('tweets_deduped')

# train 10 LDA topics using MALLET
mallet_path = '/home/royabitbol/Development/mallet/bin/mallet'
model = models.wrappers.LdaMallet(mallet_path, corpus, num_topics=10, id2word=corpus.dictionary)
# ...

# now use the trained model to infer topics on a new document
doc = "Don't sell coffee, wheat nor sugar; trade gold, oil and gas instead."
bow = corpus.dictionary.doc2bow(utils.simple_preprocess(doc))
print model[bow]  # print list of (topic id, topic weight) pairs
