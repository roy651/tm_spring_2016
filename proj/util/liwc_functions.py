from collections import Counter
from lexicons.liwc import Liwc
from db_util import ReadTweetsStr

def AnalyzeLIWC(_host, _user, _passwd, _db, _table, _name):
    all_text = ReadTweetsStr(_host, _user, _passwd, _db, _table)
    liwc_results(all_text, strip_suffix(_name))

def CorrelateLIWC(_host, _user, _passwd, _db, _table1, _table2, _name1, _name2):
    all_text1 = ReadTweetsStr(_host, _user, _passwd, _db, _table1)
    all_text2 = ReadTweetsStr(_host, _user, _passwd, _db, _table2)
    liwc_correlation(all_text1, all_text2, strip_suffix(_name1), strip_suffix(_name2))

def AnalyzeAndCorrelateLIWC(_host, _user, _passwd, _db, _table, _name, _field):
    values_text = ReadTweetsStr(_host, _user, _passwd, _db, _table, _field)
    liwc_multi_results(values_text, strip_suffix(_name))

def strip_suffix(name):
    index = name.index('.')
    return name[:index] if index > 0 else name

def liwc_multi_results(values, _name):
    index = 0
    for first_key, first_value in values.items():
        if len(values) - index <= 1:
            if len(values) == 1:
                liwc_results(first_value, _name)
            else:
                return
        else:
            for second_key, second_value in values.items()[index+1:]:
                liwc_correlation(first_value, second_value,
                                _name + '_' + str(first_key), _name + '_' + str(second_key))
        index += 1

def liwc_results(str, _name):
    liwc_lexicon = Liwc()
    #Count the number of words in each Category
    category_counts = Counter(liwc_lexicon.read_document(str))
    print 'Basic category counts: {}'.format(category_counts)
    #Calculate the score for each category
    full_counts = liwc_lexicon.summarize_document(str)
    liwc_lexicon.print_summarization(full_counts, _name)

def liwc_correlation(str1, str2, _name1, _name2):
    liwc_lexicon = Liwc()
    #Prepare the data to analysis
    full_counts1 = liwc_lexicon.summarize_document(str1)
    full_counts2 = liwc_lexicon.summarize_document(str2)
    #Calculate Correlation
    liwc_lexicon.print_analysis(full_counts1,full_counts2, _name1, _name2)
