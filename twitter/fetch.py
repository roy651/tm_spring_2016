#!/usr/bin/python
import io
import json
import twitter
import sys

# XXX: Go to http://twitter.com/apps/new to create an app and get values
# for these credentials that you'll need to provide in place of these
# empty string values that are defined as placeholders.
#
# See https://vimeo.com/79220146 for a short video that steps you
# through this process
#
# See https://dev.twitter.com/docs/auth/oauth for more information
# on Twitter's OAuth implementation.

CONSUMER_KEY = 'EGVuhW7I1u2f3Wn42cFxRfQZt'
CONSUMER_SECRET = 'geXfaxTs4TaHSBnmVxwrt1W5p3Bl6Slaj52wVsZBaMRo1n3KuW'
OAUTH_TOKEN = '29264083-X29ypI01ndSYRNoVQoZ97Qv4tkUjjCD8TihWbXpMW'
OAUTH_TOKEN_SECRET = '7ibZa2Sy6kcCpTaYHU8NTAvgRA68yzv6vPwbbV0IjnQfY'

# The keyword query

QUERY = sys.argv[1]

# The file to write output as newline-delimited JSON documents
OUT_FILE = "tmp/" + QUERY + ".json"


# Authenticate to Twitter with OAuth

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

# Create a connection to the Streaming API

twitter_stream = twitter.TwitterStream(auth=auth)


print 'Filtering the public timeline for "{0}"'.format(QUERY)

# See https://dev.twitter.com/docs/streaming-apis on keyword parameters

stream = twitter_stream.statuses.filter(track=QUERY, language='en')

# Write one tweet per line as a JSON document.

with io.open(OUT_FILE, 'w', encoding='utf-8', buffering=1) as f:
    for tweet in stream:
        f.write(unicode(u'{0}\n'.format(json.dumps(tweet, ensure_ascii=False))))
        if 'text' in tweet:
            print tweet['text']
