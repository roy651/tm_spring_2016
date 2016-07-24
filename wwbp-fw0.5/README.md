##INSTALLATION NOTES FOR UBUNTU
(tested on 14.04)

#install required ubuntu libraries
'''
sudo apt-get install mysql-server python-numpy python-scipy r-base python-singledispatch libcairo2-dev libxt-dev libxaw7-dev python-matplotlib python-pip build-essential python-dev libmysqlclient-dev python-mysqldb
'''

#install required python packages
'''
pip install rpy2 python-dateutil nltk statsmodels scikit-learn pandas SQLAlchemy wordcloud unicodecsv
'''

#install required R packages
'''
R
>install.packages('wordcloud')
>install.packages('Cairo')
>install.packages('extrafont')
>quit()
'''

#load corpus using nltk
'''
python
>>>import nltk
>>>nltk.download('wordnet')
>>>quit()
'''

#get data to work with, one recommended source:
http://u.cs.biu.ac.il/~koppel/BlogCorpus.htm

#example commands
'''
./fwInterface.py -d tweetcollectiondb -t messagestable -c user_id --add_ngrams -n 1 2 3 --feat_occ_filter --set_p_occ 0.05 --combine_feat_tables 1to3gram

./fwInterface.py -d tweetcollectiondb -t messagestable -f 'feat$1gram$messages_r5k$user_id$16to16' --feat_occ_filter --set_p_occ 0.05

./fwInterface.py -d tweetcollectiondb -t messagestable -c user_id -f 'feat$1gram$messages_r5k$user_id$16to16$0_05' --group_freq_thresh 500 --outcome_table user_data --outcomes age --outcome_controls gender --rmatrix --tagcloud --output_name TEST
'''



#My Samples:

./fwInterface.py -d text_mining -t tweets -c tweeter_id --add_ngrams -n 1 2 3 --feat_occ_filter --set_p_occ 0.05 --combine_feat_tables 1to3gram

python python/fwInterface.py -d text_mining -t tweets -c tweeter_id --encoding utf8 --add_ngrams -n 1 2 3 --feat_occ_filter --set_p_occ 0.05 --combine_feat_tables 1to3gram --message_field tweet_text --messageid_field tweet_id

python python/fwInterface.py -d text_mining -t tweets -c tweeter_id --encoding utf8 --message_field tweet_text --messageid_field tweet_id --tagcloud --make_wordclouds -f 'feat$1to3gram$tweets$tweeter_id$16to16$0_05'  --output_name TEST






#example commands for language filtering on Hadoop
./runThis.sh INPUT OUTPUT MESSAGE_FIELD LANG_CODE1[,LANG_CODE2,...]

./runThis.sh /msgs10k.csv /msgs10k.en_fr_pt 4 en,fr,pr

#example commands for part of speech tagging on Hadoop (with Penn Tree Bank, in example)
./runThis.sh INPUT OUTPUT MESSAGE_FIELD MODEL

./runThis.sh /msgs10k.csv /msgs10k.pos 4 model.ritter_ptb_alldata_fixed.20130723

#example commands for ngram extraction on Hadoop
./runThis INPUT OUTPUT MESSAGE_FIELD GROUP_ID N

./runThis.sh /messages_en.csv /feat.1gram.messages_en.user_id 2 1 1
