# Text Mining Project 
## Eran Temstet / Roy Abitbol
### Spring 2016 / Haifa University / Information Systems

```
usage: semAnalysis.py [-h] [-H HOST] [-d DB] [-u USER] [-p PASS] [-t TABLE]
                      [-f1 FILE1] [-s1 SEPERATOR1] [-g1 GROUP1] [-h1]
                      [-f2 FILE2] [-s2 SEPERATOR2] [-g2 GROUP2] [-h2] [-N]
                      [-T] [-G] [-L] [-W] [-K] [-Ti ITERATIONS]
                      [-Tt NUMTOPICS]
```

#### Examples:

```
python semAnalysis.py -f1 hiv.csv -h1
```
* Process a file with a header row - but essentially do nothing (no additional flags)
..* Removing the h1 flag will read the first line as data (instead of ignoring it)
..* Adding the -s1 flag with a seperator character allows to read files with other delimiters
..* The commend allows the processing of either one or two input files together
..* All flags with a number suffix refer to the respective index of the input file
..* Most operations work on each file separately except for -L which examines file for correlation (see below)

```
python semAnalysis.py -f1 hiv.csv -h1 -H $IP -d c9 -u root
```

..* Process a file with specified connection properties:
....* -H --host
....* -d --database
....* -u --user
....* -p --pass
....* -t --table

```
python semAnalysis.py -f1 hiv.csv -h1 -K
```
..* Process a file with a header row - And keep all intermediate DB tables after the run

```
python semAnalysis.py -f1 hiv.csv -h1 -W
```
..* Create a word-cloud from a file

```
python semAnalysis.py -f1 hiv.csv -h1 -W -g1 talk_about`
```
..* Create a word-cloud for each of the values in the group field talk_about
..* Same command works on fields: sarcasm, posted_by

```
python semAnalysis.py -f1 hiv.csv -h1 -N
```
..* Create N-grams from the input file using the tweeter_id as a grouping criteria (poor results)
    
```
python semAnalysis.py -f1 hiv.csv -h1 -N -g1 talk_about
```
..* Create N-grams from the input file using the talk_about as a grouping criteria
..* Same command works on fields: sarcasm, posted_by (see below)

```
python semAnalysis.py -f1 hiv.csv -h1 -N -g1 sarcasm
```
..* Create N-grams from the input file using the sarcasm as a grouping criteria

```
python semAnalysis.py -f1 hiv.csv -h1 -N -g1 posted_by
```
..* Create N-grams from the input file using the posted_by as a grouping criteria

```
python semAnalysis.py -f1 hiv.csv -h1 -T
```
..* Generate 50 topics from the input text file. Iterate topic generation 1000 times

```
python semAnalysis.py -f1 hiv.csv -h1 -T -G
```
..* Using the -G flag will utilize the gensim engine for topics generation instead of the mallet engine

```
python semAnalysis.py -f1 hiv.csv -h1 -T -g1 talk_about -Ti 100 -Tt 5 
```
..* Generate 5 topics for each value within the talk_about field. Iterate topic generation 100 times
..* Same command works on fields: sarcasm, posted_by (see below)
    
```
python semAnalysis.py -f1 asthma.csv -h1 -T -g1 posted_by -Ti 200 -Tt 10
```
..* Generate 10 topics for each value within the posted_by field. Iterate topic generation 200 times

```
python semAnalysis.py -f1 hiv.csv -h1 -L
```
..* Process the input file using LIWC techniques
    
```
python semAnalysis.py -f1 hiv.csv -h1 -L -g1 talk_about    
```
..* Process the input file using LIWC, for each value within the talk_about field and provide a 
..  correlation matrix for all available values combinations
..* Same command works on fields: sarcasm, posted_by

```
python semAnalysis.py -f1 hiv.csv -h1 -L -f2 asthma.csv -h2
<<<<<<< HEAD
```
..* Process the two input file using LIWC techniques and provide a correlation matrix to compare them
=======
    - Process the two input file using LIWC techniques and provide a correlation matrix to compare them
    

    
>>>>>>> 9d6c02a97b4733f50668013fda9be3ba9b1977e5
