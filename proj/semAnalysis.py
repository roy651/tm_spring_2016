#!/usr/bin/env python
###########################################################
## semAnalysis.py
##
## Interface Module to semantically analyze tweets CSV input files
##

__authors__ = "R. Abitbol, E. Temstmet @ University of Haifa, Israel"
__copyright__ = "Copyright 2016"
__credits__ = ["Einat Minkov, @ University of Haifa, Israel"]
__license__ = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-nc-sa/3.0/"
__version__ = "0.1"
__maintainer__ = ""
__email__ = ""

import os, getpass
import sys
import pdb
import argparse
import time
import logging
from pprint import pprint
from numpy import isnan, sqrt, log2
from ConfigParser import SafeConfigParser
import sys
sys.path.insert(0, 'util')
import utils_globals
from db_util import StoreDB
from db_util import DropAllTables
from dedup import DedupRecords
from runMallet import GenTopics
from wc import GenWordcloud
from ngrams import GenNGrams
from liwc_functions import AnalyzeLIWC
from liwc_functions import CorrelateLIWC
from liwc_functions import AnalyzeAndCorrelateLIWC

#################################################################
### Init constants
##
#
DEF_HOST = 'localhost'
DEF_DB = 'text_mining'
DEF_USER = 'root'
DEF_PASS = '' # 'root'
DEF_TABLE = 'twts'
DEF_HEADER1 = False
DEF_SEPERATOR1 = '\t'
DEF_GROUP1 = 'tweeter_id'
DEF_HEADER2 = False
DEF_SEPERATOR2 = '\t'
DEF_GROUP2 = 'tweeter_id'

DEF_NGRAMS = False
DEF_TOPICS = False
DEF_LIWC = False
DEF_WORDCLOUD = False
DEF_GENSIM = False
DEF_KEEPDB = False

DEF_ITERATIONS = 1000
DEF_NUM_TOPICS = 50

DEF_MESSAGE_FIELD = 'tweet_text'
DEF_MESSAGE_FIELD = 'tweet_id'

#################################################################
### Main / Command-Line Processing:
##
#
def main(fn_args = None):
    '''
    :param fn_args: string - ex "-d testing -t msgs -c user_id --add_ngrams -n 1 "
    '''
    start_time = time.time()
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)


    ##Argument Parser:
    init_parser = argparse.ArgumentParser(prefix_chars='-+', formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)

    init_args, remaining_argv = init_parser.parse_known_args()

    # Inherit options from init_parserDEF_MESSAGEID_FIELD_ID
    parser = argparse.ArgumentParser(description='Extract and Manage Tweets Feature Data.',
        parents=[init_parser])

    group = parser.add_argument_group('Input files', 'Defining the format of the files from which features are extracted.')

    group.add_argument('-H', '--host', metavar='HOST', dest='host', default=DEF_HOST,
                       help='Host that the mysql server runs on (default: %s)' % DEF_HOST)
    group.add_argument('-d', '--db', metavar='DB', dest='db', default=DEF_DB,
                        help='Target Database Name.')
    group.add_argument('-u', '--user', metavar='USER', dest='user', default=DEF_USER,
                        help='Database user name.')
    group.add_argument('-p', '--pass', metavar='PASS', dest='passwd', default=DEF_PASS,
                        help='Database user password.')
    group.add_argument('-t', '--table', metavar='TABLE', dest='table', default=DEF_TABLE,
                        help='Target Table.')
    group.add_argument('-f1', '--file1', metavar='FILE1', dest='file1',
                        help='First input file to be processes (in CSV format with first row as field headers)')
    group.add_argument('-s1', '--seperator1', metavar='SEPERATOR1', dest='seperator1', default=DEF_SEPERATOR1,
                        help='Seperator token for the first input file')
    group.add_argument('-g1', '--group1', metavar='GROUP1', dest='group1', default=DEF_GROUP1,
                        help='Group by field for the first input file - used by n-grams and liwc')
    group.add_argument('-h1', '--headers1', action='store_true', dest='header1', default=DEF_HEADER1,
                        help='Flag indicating whether the first input file has headers)')
    group.add_argument('-f2', '--file2', metavar='FILE2', dest='file2',
                        help='Second (optional) input file to be processes (in CSV format with first row as field headers)')
    group.add_argument('-s2', '--seperator2', metavar='SEPERATOR2', dest='seperator2', default=DEF_SEPERATOR2,
                        help='Seperator token for the second input file')
    group.add_argument('-g2', '--group2', metavar='GROUP2', dest='group2', default=DEF_GROUP2,
                        help='Group by field for the second input file - used by n-grams and liwc')
    group.add_argument('-h2', '--headers2', action='store_true', dest='header2', default=DEF_HEADER2,
                        help='Flag indicating whether the second input file has headers)')

    group.add_argument('-N', '--ngrams', action='store_true', dest='ngrams', default=DEF_NGRAMS,
                        help='Generate 1-2-3-grams true or false')
    group.add_argument('-T', '--topics', action='store_true', dest='topics', default=DEF_TOPICS,
                        help='Generate topics true or false')
    group.add_argument('-G', '--gensim', action='store_true', dest='gensim', default=DEF_GENSIM,
                        help='Utilize Gensim for topics generation instead of Mallet true or false')
    group.add_argument('-L', '--liwc', action='store_true', dest='liwc', default=DEF_LIWC,
                        help='Generate LIWC true or false')
    group.add_argument('-W', '--wordcloud', action='store_true', dest='wordcloud', default=DEF_WORDCLOUD,
                        help='Generate Word Cloud true or false')
    group.add_argument('-K', '--keepdb', action='store_true', dest='keepdb', default=DEF_KEEPDB,
                        help='Keep DB tables at the end of the run')

    group.add_argument('-Ti', '--iterations', metavar='ITERATIONS', dest='iterations', default=DEF_ITERATIONS,
                        help='Num of iterations for topic generation')
    group.add_argument('-Tt', '--num_topics', metavar='NUMTOPICS', dest='num_topics', default=DEF_NUM_TOPICS,
                        help='Num of topics to generate')

    # group.add_argument('--message_field', metavar='FIELD', dest='message_field', default=DEF_MESSAGE_FIELD,
    #                     help='The field where the text to be analyzed is located.')
    # group.add_argument('--messageid_field', metavar='FIELDID', dest='messageid_field', default=DEF_MESSAGEID_FIELD_ID,
    #                     help='The unique identifier for the message.')

    if fn_args:
        args = parser.parse_args(fn_args.split())
    else:
        args = parser.parse_args(remaining_argv)


    ##Process Arguments
    # def FE():
    #     return FeatureExtractor(args.corpdb, args.corptable, args.correl_field, args.mysql_host, args.message_field, args.messageid_field, args.encoding, args.nounicode, args.lexicondb, wordTable = args.wordTable)
    #
    # def SE():
    #     return SemanticsExtractor(args.corpdb, args.corptable, args.correl_field, args.mysql_host, args.message_field, args.messageid_field, args.encoding, args.nounicode, args.lexicondb, args.corpdir, wordTable = args.wordTable)

    utils_globals.UNIQUE_ID = curr_time = str(int(round(time.time() * 1000)))
    output_folder = 'output/' + curr_time + '/'
    utils_globals.BASE_DIR = orig_folder = os.getcwd()
    os.makedirs(output_folder)

    deduped_table1 = None
    if args.file1:
        table_name = args.table + '_' + curr_time + '_1f'
        #### Load into DB
        StoreDB(args.host, args.user, args.passwd, args.db, table_name, args.file1, args.header1, args.seperator1)
        #### Clear duplicate records
        deduped_table1 = DedupRecords(args.host, args.user, args.passwd, args.db, table_name)
        os.chdir(output_folder)
        #### Generate liwc
        if args.liwc:
            if args.group1 != DEF_GROUP1:
                AnalyzeAndCorrelateLIWC(args.host, args.user, args.passwd, args.db, deduped_table1, args.file1, args.group1)
            else:
                AnalyzeLIWC(args.host, args.user, args.passwd, args.db, deduped_table1, args.file1)
        #### Generate topics
        if args.topics:
            GenTopics(args.host, args.user, args.passwd, args.db, deduped_table1, args.group1, int(args.iterations), int(args.num_topics), args.gensim)
        if args.wordcloud:
            GenWordcloud(args.host, args.user, args.passwd, args.db, deduped_table1, args.file1, args.group1)
        if args.ngrams:
            GenNGrams(args.host, args.user, args.passwd, args.db, deduped_table1, args.group1)

    os.chdir(orig_folder)
    deduped_table2 = None
    if args.file2:
        table_name = args.table + '_' + curr_time + '_2f'
        #### Load into DB
        StoreDB(args.host, args.user, args.passwd, args.db, table_name, args.file2, args.header2, args.seperator2)
        #### Clear duplicate records
        deduped_table2 = DedupRecords(args.host, args.user, args.passwd, args.db, table_name)
        os.chdir(output_folder)
        #### Generate liwc
        if args.liwc:
            if args.group2 != DEF_GROUP2:
                AnalyzeAndCorrelateLIWC(args.host, args.user, args.passwd, args.db, deduped_table2, args.file2, args.group2)
            else:
                AnalyzeLIWC(args.host, args.user, args.passwd, args.db, deduped_table2, args.file2)
        #### Generate topics
        if args.topics:
            GenTopics(args.host, args.user, args.passwd, args.db, deduped_table2, args.group2, int(args.iterations), int(args.num_topics), args.gensim)
        if args.wordcloud:
            GenWordcloud(args.host, args.user, args.passwd, args.db, deduped_table2, args.file2, args.group2)
        if args.ngrams:
            GenNGrams(args.host, args.user, args.passwd, args.db, deduped_table2, args.group2)

    if args.file1 and args.file2 and args.liwc:
        #### Correlate liwc
        CorrelateLIWC(args.host, args.user, args.passwd, args.db, deduped_table1, deduped_table2, args.file1, args.file2)

    if not args.keepdb:
        DropAllTables(args.host, args.user, args.passwd, args.db)


if __name__ == "__main__":
    main()
    sys.exit(0)
