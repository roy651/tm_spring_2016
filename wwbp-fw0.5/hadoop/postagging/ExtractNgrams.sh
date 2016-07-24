#! /bin/bash

################### environment variables ######
source /classpath.sh

################### compile the code ###########
##### useful on commandline and for documentation but not executed
cd /classes
source /classpath.sh
javac -d . ../ExtractNgrams.java
rm ExtractNgrams.jar && jar -cvf ExtractNgrams.jar -C . .

########### one liner that does everything at once:
javac -d . ../ExtractNgrams.java;rm ExtractNgrams.jar && jar -cvf ExtractNgrams.jar -C . .;hadoop jar ExtractNgrams.jar org.wwbp.ExtractNgrams -libjars "$libjars" -input /m2014feb.csv -output /out/ -message_field 4 -group_id_index 1 -n 2

############## run code on local machine
javac -d . ../ExtractNgrams.java;rm ExtractNgrams.jar && jar -cvf ExtractNgrams.jar -C . .;java org.wwbp.ExtractNgrams /m2014feb.csv out



################# required libraries ########
# opencsv
libjars="${libjars},/home/hadoop/shrik/src/opencsv-2.3/deploy/opencsv-2.3.jar"
libjars="${libjars},/home/hadoop/shrik/src/ark-tweet-nlp-0.3.2/ark-tweet-nlp-0.3.2.jar"