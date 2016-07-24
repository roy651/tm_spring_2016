# -*- coding: utf-8 -*-
import re
import numpy
from lexicons.base import Lexicon
from collections import Counter
import json
import os

class Liwc(Lexicon):
    corpus_filepath = os.path.dirname(os.path.abspath(__file__)) + '/LIWC2015_English_trie.trie'

    # category analysis variables:
    category_keys = ['function (Function Words)',
					'pronoun (Pronouns)',
					'ppron (Personal Pronouns)',
					'i (I)',
					'we (We)',
					'you (You)',
					'shehe (SheHe)',
					'they (They)',
					'ipron (Impersonal Pronouns)',
					'article (Articles)',
					'prep (Prepositions)',
					'auxverb (Auxiliary Verbs)',
					'adverb (Adverbs)',
					'conj (Conjunctions)',
					'negate (Negations)',
					'verb (Verbs)',
					'adj (Adjectives)',
					'compare (Comparisons)',
					'interrog (Interrogatives)',
					'number (Numbers)',
					'quant (Quantifiers)',
					'affect (Affect)',
					'posemo (Positive Emotions)',
					'negemo (Negative Emotions)',
					'anx (Anx)',
					'anger (Anger)',
					'sad (Sad)',
					'social (Social)',
					'family (Family)',
					'friend (Friends)',
					'female (Female)',
					'male (Male)',
					'cogproc (Cognitive Processes)',
					'insight (Insight)',
					'cause (Causal)',
					'discrep (Discrepancies)',
					'tentat (Tentative)',
					'certain (Certainty)',
					'differ (Differentiation)',
					'percept (Perceptual Processes)',
					'see (See)',
					'hear (Hear)',
					'feel (Feel)',
					'bio (Biological Processes)',
					'body (Body)',
					'health (Health)',
					'sexual (Sexual)',
					'ingest (Ingest)',
					'drives (Drives)',
					'affiliation (Affiliation)',
					'achieve (Achievement)',
					'power (Power)',
					'reward (Reward)',
					'risk (Risk)',
					'focuspast (Past Focus)',
					'focuspresent (Present Focus)',
					'focusfuture (Future Focus)',
					'relativ (Relativity)',
					'motion (Motion)',
					'space (Space)',
					'time (Time)',
					'work (Work)',
					'leisure (Leisure)',
					'home (Home)',
					'money (Money)',
					'relig (Religion)',
					'death (Death)',
					'informal (Informal Language)',
					'swear (Swear)',
					'netspeak (Netspeak)',
					'assent (Assent)',
					'nonflu (Nonfluencies)',
					'filler (Filler Words)']

    # full analysis variables:
    meta_keys = ['WC', 'WPS', 'Sixltr', 'Dic', 'Numerals']
    puncuation_keys = [
        'Period', 'Comma', 'Colon', 'SemiC', 'QMark', 'Exclam',
        'Dash', 'Quote', 'Apostro', 'Parenth', 'OtherP', 'AllPct']
    punctuation = [
        ('Period', '.'),
        ('Comma', ','),
        ('Colon', ':'),
        ('SemiC', ';'),
        ('QMark', '?'),
        ('Exclam', '!'),
        ('Dash', '-'),  # –—
        ('Quote', '"'),  # “”
        ('Apostro', "'"),  # ‘’
        ('Parenth', '()[]{}'),
        ('OtherP', '#$%&*+-/<=>@\\^_`|~')
    ]

    def __init__(self):
        self.all_keys = self.meta_keys + self.category_keys[:-1] + self.puncuation_keys

        with open(self.corpus_filepath) as corpus_file:
            self._trie = json.load(corpus_file)

    # standard Lexicon functionality:
    def read_token(self, token, token_i=0, trie_cursor=None):
        if trie_cursor is None:
            trie_cursor = self._trie

        if '*' in trie_cursor:
            for category in trie_cursor['*']:
                yield category
        elif '$' in trie_cursor and token_i == len(token):
            for category in trie_cursor['$']:
                yield category
        elif token_i < len(token):
            letter = token[token_i]
            if letter in trie_cursor:
                for category in self.read_token(token, token_i + 1, trie_cursor[letter]):
                    yield category

    def read_document(self, document, token_pattern=r"[a-z]['a-z]*"):
        for match in re.finditer(token_pattern, document.lower()):
            for category in self.read_token(match.group(0)):
                yield category

    # extra (legacy) Liwc functionality:
    def summarize_document(self, document, token_pattern=r"[a-z]['a-z]*", normalize=True):
        sentence_count = len(re.findall(r"[.!?]+", document)) or 1

        # tokens is a bit redundant because it duplicates the tokenizing done
        # in read_document, but to keep read_document simple, we just run it again here.
        tokens = re.findall(token_pattern, document.lower())
        counts = Counter(self.read_document(document, token_pattern=token_pattern))
        counts['Dic'] = sum(counts.values())
        counts['WC'] = len(tokens)
        counts['WPS'] = counts['WC'] / float(sentence_count)
        counts['Sixltr'] = sum(len(token) > 6 for token in tokens)
        counts['Numerals'] = sum(token.isdigit() for token in tokens)

        # count up all characters so that we can get punctuation counts quickly
        character_counts = Counter(document)
        for name, chars in self.punctuation:
            counts[name] = sum(character_counts[char] for char in chars)
        # Parenth is special -- we only count one half of them (to match the official LIWC application)
        counts['Parenth'] = counts['Parenth'] / 2.0
        counts['AllPct'] = sum(counts[name] for name, _ in self.punctuation)

        if normalize:
            # normalize all counts but the first two ('WC' and 'WPS')
            for column in self.all_keys[2:]:
                counts[column] = float(counts[column]) / float(counts['WC'])

        # return a normal dict() rather than the Counter() instance
        result = dict.fromkeys(self.category_keys + ['Dic'], 0)
        result.update(counts)
        return result


    def print_summarization(self, counts, _name):
        f = open('liwc_results_' + _name + '.csv', 'w')
        absolutes = ['%d' % counts['WC'], '%0.2f' % counts['WPS']]
        percentages = ['%0.2f' % (counts[key] * 100) for key in self.all_keys[2:]]
        for key, value in zip(self.all_keys, absolutes + percentages):
            f.write('%s,' % (key))
            print '%16s %s' % (key, value)
        f.close()
        f = open('liwc_results_' + _name + '.csv', 'a')
        f.write("\n")
        for key, value in zip(self.all_keys, absolutes + percentages):
            f.write('%s,' % (value))
        f.close()

    def print_analysis(self,full_counts1,full_counts2, _name1, _name2):
        f2 = open('liwc_lireg_' + _name1 + '_' + _name2 + '.csv', 'w')
        ana1=[]
        ana2=[]
        absolutes = ['%d' % full_counts1['WC'], '%0.2f' % full_counts1['WPS']]
        percentages = ['%0.2f' % (full_counts1[key] * 100) for key in self.all_keys[2:]]
        f2.write('TYPE,')
        for key, value in zip(self.all_keys, absolutes + percentages):
            ana1.append(float(value))
            f2.write('%s,' % (key))

        f2.write("\n")
        f2.write('%s,' % (_name1))
        for key, value in zip(self.all_keys, absolutes + percentages):
            f2.write('%s,' % (value))

        absolutes = ['%d' % full_counts2['WC'], '%0.2f' % full_counts2['WPS']]
        percentages = ['%0.2f' % (full_counts2[key] * 100) for key in self.all_keys[2:]]
        f2.write("\n")
        f2.write('%s,' % (_name2))
        for key, value in zip(self.all_keys, absolutes + percentages):
            ana2.append(float(value))
            f2.write('%s,' % (value))

        x = numpy.array([0, 1])
        f2.write("\n")
        f2.write('LIREG,')
        y = numpy.array([ana1[6:],ana2[6:]])
        A = numpy.vstack([x, numpy.ones(len(x))]).T
        m, c = numpy.linalg.lstsq(A, y)[0]
        print(m, c)
        index = 0
        for key, value in zip(self.all_keys, absolutes + percentages):
            if (index < 6):
                f2.write('NA,')
                print '%16s %s' % (key, 'NA')
            else:
                f2.write('%s,' % (m[index-6]))
                print '%16s %s' % (key, m[index-6])
            index += 1
        f2.write("\n")
        f2.write('Positive = greater %s\nNegative = greater %s' % (_name2, _name1))
        f2.close()

        print numpy.corrcoef(ana1[6:],ana2[6:])
        f = open('liwc_correlation_' + _name1 + '_' + _name2 + '.csv', 'w')
        f.write("Liwc Correlation:\n" + str(numpy.corrcoef(ana1[6:],ana2[6:])))
        f.close()
