import re
import gensim
import os
import os.path
import sys
import itertools
import numpy as np
import util
import argparse
from util import combination_index

import logging

parser = argparse.ArgumentParser("Word2Vec")

def get_vector_from_model(model, key):
    try:
        res = model[key]
    except:
        res = np.zeros(model.vector_size)
    return res



''''''
from pprint import pprint   # pretty-printer



if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
 
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    # Train word2vec model
    #dir = 'data/ck12-multi-line-txt/'
    #dir = 'data/wikipedia_content_based_on_ck_12_keyword_v1/'
    path_model = '../model/word2vec_21.model'
    #lst_sentence = util.get_sentence(dir)


    sents = util.read_ck_txt ([

        '../data/ck12foundation.txt.merged', 
        '../data/ck_keywords.txt',
        '../data/ohio8grade-science.txt.merged',


        #'../wikifiles/tt.txt',
      #  '../data/ck12-ls-concepts.txt.merged',   
      #  '../data/ck12-ls.txt.merged',    
      #  '../data/ck12-ps-concepts.txt.merged',
      #  '../data/ck12-ps.txt.merged'
        ])
 
    #print util.join_list(sents)
    print 'done reading sentences'

    #dictionary = gensim.corpora.Dictionary(sents)
    #dictionary.save('/tmp/deerwester.dict') # store the dictionary, for future reference
    #pprint(dictionary)

    #lens = [len(x) for x in lst_sentence]
    #lens = [x for x in lst_sentence if len(x) == 2]
    #pprint(lst_sentence)
    #print lens

 
    #sents = enlarge_window(sents, 1)
    #for s in sents:
    #    print s

    #bigram_transformer = gensim.models.Phrases(sents)
    #sents = bigram_transformer[sents]

    #window = 11 (976, more ig better), iter = 30 
    #iter=30 -> window = 15, size = 400 (962) -> window=15, size=500 (979)
    #iter = 40 -> window = 15, size = 500 (981)

    #iter = 30, win = 17, size=600 (964) -> size more?
    model = gensim.models.Word2Vec(sents, min_count = 2, workers = 4, size = 400, window = 11, iter = 30)
    model.save(path_model)

''''''
# Test model on train data
#path_model = 'model/word2vec_21.model'
#test_on_train(path_model, n_combination_question = 3, n_combination_answer = 3, n_word_question = 5)
#test_on_validation(path_model, n_combination_question = 3, n_combination_answer = 3, n_word_question = 5)
#print combination_index(10, 3)
