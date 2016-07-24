#!/bin/bash

# Getting working directory
WD=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo $WD


if [ $# -ne 4 ]
then
    echo "./runThisLocally.sh INPUT OUTPUT MESSAGE_FIELD [MODEL]"
    echo "Example for Penn Tree Bank annotations"
    echo "./runThisLocally.sh /msgs10k.csv /msgs10k.pos 4 model.ritter_ptb_alldata_fixed.20130723"
    echo "Example for Tweet-style tags"
    echo "./runThisLocally.sh /msgs10k.csv /msgs10k.pos 4 model.20120919"
    exit 1
fi

input="$1"
output="$2"
message_field="$3"
model="$4"
files="/ark-pos-models/$model"

if [ ! -f "$files" ]
then
    echo "$files doesn't exist"
    exit
fi

source "$WD/classpath.sh"

cd "$WD/classes"

javac -d . ../TweetParser.java || exit

rm TweetParser.jar ; jar -cvf TweetParser.jar -C . .

echo hadoop jar TweetParser.jar org.wwbp.TweetParser -libjars "$libjars" -files "$files" -input "$input" -output "$output" -message_field "$message_field" -model "$model" -testing

hadoop jar TweetParser.jar org.wwbp.TweetParser \
    -libjars "$libjars" \
    -files "$files" \
    -input "$input" \
    -output "$output" \
    -message_field "$message_field" \
    -model "$model" \
    -testing