import subprocess
import utils_globals
from db_util import GetAllTableNames
import re
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import pandas as pd
from dedup import SarcasmStr
from dedup import PostedByStr
from dedup import TalkAboutStr

def GenNGrams(_host, _user, _pass, _db, _table, _group):
    if _group in ['talk_about', 'sarcasm', 'posted_by']:
        _group += '_i'
    cmd = ['python', utils_globals.BASE_DIR + '/../wwbp-fw0.5/python/fwInterface.py', '-d', _db,
            '-t', _table, '-c', _group, '--encoding', 'utf8', '--add_ngrams',
            '-n', '1', '2', '3',
            '--feat_occ_filter', '--set_p_occ', '0.05',
            '--combine_feat_tables', '1to3gram',
            '--group_freq_thresh', '10',
            '--message_field', 'tweet_text', '--messageid_field', 'tweet_id']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process.wait()
    for line in process.stdout:
        print(line)

    allTables = GetAllTableNames(_host, _user, _pass, _db)
    export_table_to_csv(_host, _user, _pass, _db,
                        filter_pick([x for (x,) in allTables], '.*\$\dgram\$.*' + utils_globals.UNIQUE_ID + '.*'))

def export_table_to_csv(_host, _user, _pass, _db, table_names):
    db_url = URL(drivername='mysql', host=_host,
                database=_db, username=_user,
                password=_pass)
    eng = create_engine(db_url)
    re_sarcasm = re.compile('sarcasm_i')
    re_talk_about = re.compile('talk_about_i')
    re_posted_by = re.compile('posted_by_i')

    for table in table_names:
        df = pd.read_sql_table(table_name=table, con=eng, schema=_db)
        if re_sarcasm.search(table):
            df['sarcasm'] = df['group_id'].apply(SarcasmStr)
        if re_talk_about.search(table):
            df['talk_about'] = df['group_id'].apply(TalkAboutStr)
        if re_posted_by.search(table):
            df['posted_by'] = df['group_id'].apply(PostedByStr)
        df.drop('group_norm', axis=1, inplace=True)
        # filtering values over 4 - consider changing this...
        df[df['value'] > 4].to_csv(path_or_buf=table+".csv", index=False)

def filter_pick(lines, regex):
    filter = re.compile(regex).search
    return [ l for l in lines for m in (filter(l),) if m]
