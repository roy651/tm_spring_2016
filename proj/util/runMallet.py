# set up logging so we see what's going on
import logging
import os
import MySQLdb
import traceback
import utils_globals
from gensim import corpora, models, utils
from db_util import GetDistinctValues
logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

def iter_rows(_host, _user, _passwd, _db, _table, _group, _value):
    """Iterate over all the table rows, yielding one row at a time."""
    try:
        mydb = MySQLdb.connect(host=_host,
        user=_user,
        passwd=_passwd,
        db=_db)

        cursor = mydb.cursor()
        # Prepare SQL query
        sql = "SELECT tweet_text FROM %s" % (_table)
        if _group is not None:
            sql += " WHERE %s = '%s'" % (_group, _value)

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
    def __init__(self, _host, _user, _passwd, _db, _table, _group=None, _value=None):
        self.value = _value
        self.group = _group
        self.table = _table
        self.db = _db
        self.passwd = _passwd
        self.user = _user
        self.host = _host
        self.dictionary = corpora.Dictionary(iter_rows(self.host, self.user, 
                                             self.passwd, self.db, self.table, 
                                             self.group, self.value))
        stoplist = set("for a of the and to in is with for an in that this it have just when be it's cant amp at on 3 http https & * ; ... # | - ! ? / , : rt . https://t.co co are th if he we his him has".split())
        stop_ids = [self.dictionary.token2id[stopword] for stopword in stoplist if stopword in self.dictionary.token2id]
        self.dictionary.filter_tokens(stop_ids)
        self.dictionary.filter_extremes()  # remove stopwords etc

    def __iter__(self):
        for tokens in iter_rows(self.host, self.user, self.passwd, self.db, 
                                self.table, self.group, self.value):
            yield self.dictionary.doc2bow(tokens)

def GenTopics(_host, _user, _passwd, _db, _table, _group, _iterations, _num_topics, _useGensim=False):
    if _group in ['talk_about', 'sarcasm', 'posted_by']:
        values = GetDistinctValues(_host, _user, _passwd, _db, _table, _group)

        for group_value in values:
            # set up the streamed corpus
            corpus = InitCorpus(_host, _user, _passwd, _db, _table, _group, group_value)
            run_mallet(corpus, _iterations, _num_topics, _useGensim, _group, group_value)
    else:
        corpus = InitCorpus(_host, _user, _passwd, _db, _table)
        run_mallet(corpus, _iterations, _num_topics, _useGensim)
        
      
def run_mallet(_corpus, _iterations, _num_topics, _useGensim, _group=None, _value=None):
    # train LDA topics
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    suffix = '_' + _group + '_' + _value if _group is not None else ''
    print "GENERATING TOPICS: " + suffix

    model = None
    try:
        if _useGensim:
            model = models.LdaModel(_corpus, num_topics=_num_topics, id2word=_corpus.dictionary, passes=_iterations)
        else:
            mallet_path = utils_globals.BASE_DIR + '/../mallet/bin/mallet'
            model = models.wrappers.LdaMallet(mallet_path, _corpus, num_topics=_num_topics, id2word=_corpus.dictionary, iterations=_iterations)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return
    
    # now use the trained model to infer topics on a new document
    # doc = "Don't sell coffee, wheat nor sugar; trade gold, oil and gas instead."
    # bow = corpus.dictionary.doc2bow(utils.simple_preprocess(doc))
    # print model[bow]  # print list of (topic id, topic weight) pairs

    # print model.show_topics(num_topics=50, num_words=10, log=False, formatted=True)

    ft = open('topics' + suffix + '.csv', 'w')
    fp = open('topicsProb' + suffix + '.csv', 'w')
    i = 0
    # We print the topics
    for topic in model.show_topics(num_topics=_num_topics, formatted=False, num_words=10):
        i = i + 1
        print "Topic #" + str(i) + ":",
        ft.write(str(i))
        for p, id in topic:
            ft.write(",%s" % (id))
            fp.write("%s,%s,%s\n" %(str(i), id, p))
        ft.write("\n")

    ft.close
    fp.close
