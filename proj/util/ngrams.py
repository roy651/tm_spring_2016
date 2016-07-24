def GenNGrams(_host, _user, _pass, _db, _name, _group):
            cmd = ['python', '../wwbp-fw0.5/python/fwInterface.py', '-d', _db,
                    '-t', deduped_table1, '-c', _group, '--encoding', 'utf8', '--add_ngrams',
                    '-n', '1', '2', '3',
                    '--feat_occ_filter', '--set_p_occ', '0.05',
                    '--combine_feat_tables', '1to3gram',
                    '--group_freq_thresh', '100',
                    '--message_field', 'tweet_text', '--messageid_field', 'tweet_id']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            process.wait()
            for line in process.stdout:
                print(line)
