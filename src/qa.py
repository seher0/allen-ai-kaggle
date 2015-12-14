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

num_misses = []

def line2sents (q, num):
    s = util.line2sents(q, num)

    return s

def get_vector_from_model(model, key):
    global num_misses

    res = np.zeros(model.vector_size)

    try:
        res = model[key]

        #print res
    except:
        num_misses.append(key)
        
    return res


def get_ans_index(ans):
    ans = ans.lower()
    return ord(ans) - ord('a')

def index2ans(ind):
    return str( unichr(ord('a') + ind) ).upper()

def cos_similar(v1, v2):
    cosine_similarity = np.dot(v1,v2)/(np.linalg.norm(v1)* np.linalg.norm(v2))
    return cosine_similarity

def get_sentence_vec(model, sent, normal=True):

    #print 'get_sentence_vec', sent
    #bigram_transformer = gensim.models.Phrases(sent)
    #sent = bigram_transformer[sent]
    #print sent

    v = [get_vector_from_model(model, w) for w in sent]
    #print v
    vec = np.sum(v, axis = 0)
    if normal:  
        N = 1 #len(v)
    else:
        N = np.max(v, axis = 0)

    vec = vec / N
    return vec

def find_qwords_similar_to_answer(model, awords, vec_a, qlist):
    print '\nANS: ' + ' '.join(awords)
    res = []
    for qw in qlist:
        vec_q = get_vector_from_model(model, qw)

        score = cos_similar(vec_q, vec_a)
        #print 'word = ', qw , ', score = ', score
        if score > 0:
            res.append( (score, qw))

    res = sorted(res,key=lambda x: x[0], reverse=True)
    
    print res
    
    return res


nltk_cache = {}
taglist = ['NN', 'NNS', 'VBG']

import nltk
def relevant_words_from_q (qlist):
    res = []
    res2 = []
    for qw in qlist:
        if qw not in nltk_cache:
            text = nltk.word_tokenize(qw)
            pos = nltk.pos_tag(text)
            nltk_cache[qw] = pos
            #print 'pos tag --- ', qw, pos
        else:
            pos = nltk_cache[qw]

        if pos[0][1] in  taglist:
            res.append (qw)
        res2.append (pos)

    return res, res2


def guess (model, question, choices, corr_ans):

    qwords = line2sents(question,2)
    qlist = util.join_list(qwords)


    if len(qlist) == 0:
        qwords = line2sents(question,-1)
        qlist = util.join_list(qwords)
    

    if use_relevant_words:
        qlist1, postags = relevant_words_from_q(qlist)
        if len(qlist1) != 0:
            qlist = qlist1
        else:
            print ("** problem: ", qlist, postags)
    
    

    #print '\n\nqlist: ', qlist

    showstr = '\n\n**********Q ' + str(qlist)
    print showstr

    vec_q = get_sentence_vec(model, qlist)
 
    #print vec_q


    ai = get_ans_index(corr_ans)
    #print ai

    max1 = -1000000
    max2 = -1000000

    ans2 = -1
    ans=-1
    ans3 = -1

    min1 = 10000000
    ansmin = -1

    sim_anss = []
    for i, c in enumerate(choices):
        cwords = line2sents(c,-1)
        cwords = cwords[0]
        vec_a = get_sentence_vec(model, cwords)


        #find_qwords_similar_to_answer(model, cwords, vec_a, qlist)

        #print 'vec a ', vec_a
        score = cos_similar(vec_q,vec_a)
        showstr =  showstr + '\nscore: ' + str(score) + ' cwords' + str(cwords)
        if score > max1 :
            max2 = max1
            max1 = score
            ans3 = ans2
            ans2 = ans
            ans = i
        if score < min1:
            ansmin = i
            min1 = score


    reststr  = '\nthey = ' + index2ans(ai) + ', we = ' + index2ans(ans)
    if ai != ans:
        #print sim_anss
        #'\n'.join(sim_anss)
        print reststr
        print max1, index2ans(ans)
        print max2, index2ans(ans2)

    showstr += reststr
    return (showstr, ai, ans, ans2, ans3, max1, max2)

import random

def do_qa(model, train_data, validate=False):
    correct_cnt = 0
    total_cnt = 0
    answers = []

    for index, line in enumerate(open(train_data)):

        if index == 0:
            continue
        else:
            lst = line.lower().strip('\n').split('\t')
            total_cnt += 1

            question = lst[1]
            if validate:
                lst_choice = lst[2:]
                correct_ans = 'U'
            else:
                correct_ans = lst[2]
                lst_choice = lst[3:]

            (showstr, their, our1, our2, our3, max1, max2) = guess (model, question, lst_choice, correct_ans)
            our = our1

            #if max1 - max2 < 0.008:
            #    ourl = [our1, our2]
            #    our = random.choice(ourl)

            answers.append ( (lst[0], index2ans(our), showstr ) )

            #if their == our or their == our2 or their == our3:
            if their == our:
                correct_cnt += 1
            else:
                pass
                #print showstr

    return (answers,correct_cnt, total_cnt)




def run_model (model_path, data = '../data/training_set.tsv', validate = False):
    print ('**** Running model from ', model_path)
    m = gensim.models.Word2Vec.load(model_path)
    answers, corr_cnt, total_cnt = do_qa(m, data, validate)

    print 'correct counts = ', corr_cnt, total_cnt

    return answers



def diff_models (model1, model2):
    res1 = run_model(model1)
    res2 = run_model(model2)

    diff = [ (x,y) for x,y in zip(res1,res2) if x[1] != y[1] ]

     #print diff
    for x, y in diff:
        print x[2]
        print y[2]
        print '==========================='
    print len(diff)
    return diff

def gen_submission(model):

    answers = run_model(model,'../data/validation_set.tsv', True)

    with open('my_submission.csv', 'w') as f:
        f.write('id,correctAnswer\n')
        for a in answers:
            f.write( str(a[0]) + ',' + a[1] + '\n')


use_relevant_words = False

if __name__ == '__main__':
    #print sys.argv
    #sys.exit(0)
    '''
    if len(sys.argv) == 2:
        path_model = sys.argv[1]
    else:
        path_model = '../model/word2vec_21.model'
    '''
    
    diff_models('../model/word2vec_21.model', '../model/word2vec-good.model')
   

    #gen_submission('../model/word2vec-good.model')


