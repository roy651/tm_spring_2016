#!/bin/bash
echo "Running Language Filter Test"
# ./runThisLocally.sh "input" "output" "message_field"
input="$1"
output="$2"
message_field="$3"
source classpath.sh


cd classes
javac -d . ../LanguageFilter.java || exit
rm LanguageFilter.jar && jar -cvf LanguageFilter.jar -C . .
echo "----------------------"
java org.wwbp.languageFilter.LanguageFilter \
-libjars "$libjars" \
-input "$input" \
-output "$output" \
-message_field "$message_field" \
-testing

