import pandas as pd
import sys

# A text file with one tweet per line

QUERY = sys.argv[1]

# The file to read input as newline-delimited JSON documents
DATA_FILE = "tmp/" + QUERY + ".json"

# Build a JSON array

data = "[{0}]".format(",".join([l for l in open(DATA_FILE).readlines()]))

# Create a pandas DataFrame (think: 2-dimensional table) to get a
# spreadsheet-like interface into the data

df = pd.read_json(data, orient='records')

print "Successfully imported", len(df), "tweets"

# Printing a DataFrame shows how pandas exposes a columnar view of the data
# print df

# Observe the "limit" field that reflects "limit notices" where the streaming API
# couldn't return more than 1% of the firehose.
# See https://dev.twitter.com/docs/streaming-apis/messages#Limit_notices_limit

# Remove the limit notice column from the DataFrame entirely

df = df[pd.notnull(df['id'])]

###############################################################################
# Create a time-based index on the tweets for time series analysis
# on the created_at field of the existing DataFrame.
df.set_index('created_at', drop=False, inplace=True)

# Get a sense of the time range for the data
print "First tweet timestamp (UTC)", df['created_at'][0]
print "Last tweet timestamp (UTC) ", df['created_at'][-1]

###############################################################################
from collections import Counter

# The "user" field is a record (dictionary), and we can pop it off
# and then use the Series constructor to make it easy to use with pandas.

user_col = df.pop('user').apply(pd.Series)

# Get the screen name column
authors = user_col.screen_name

# And count things
authors_counter = Counter(authors.values)

# And tally the totals

print
print "Most frequent (top 25) authors of tweets"
print '\n'.join(["{0}\t{1}".format(a, f) for a, f in authors_counter.most_common(25)])
print

# Get only the unique authors

num_unique_authors = len(set(authors.values))
print "There are {0} unique authors out of {1} tweets".format(num_unique_authors, len(df))

###############################################################################
# Let's just look at the content of the English tweets by extracting it
# out as a list of text
import nltk
from collections import Counter

en_text = df[df['lang'] == 'en'].pop('text')

tokens = []
for txt in en_text.values:
    tokens.extend([t.lower().strip(":,.") for t in txt.split()])

# Use a Counter to construct frequency tuples
tokens_counter = Counter(tokens)

# Display some of the most commonly occurring tokens
print tokens_counter.most_common(50)

###############################################################################

# Download the stopwords list into NLTK

nltk.download('stopwords')

# Remove stopwords to decrease noise
for t in nltk.corpus.stopwords.words('english'):
    if t in tokens_counter:
        tokens_counter.pop(t)

# Redisplay the data (and then some)
print tokens_counter.most_common(200)

###############################################################################
nltk_text = nltk.Text(tokens)
nltk_text.collocations()

###############################################################################
nltk_text.concordance("hiv")
