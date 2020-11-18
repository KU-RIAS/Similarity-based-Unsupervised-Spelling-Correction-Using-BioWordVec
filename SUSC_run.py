# -*- coding: utf-8 -*-

"""

@ author: Taehyeong Kim
@ e-mail: taehyeong93@korea.ac.kr

"""

import argparse

parser = argparse.ArgumentParser(description='Similarity-based Unsupervised Spelling Correction Using BioWordVec')
parser.add_argument('--data', type=str, help='Data', default='sample.csv')
parser.add_argument('--similar_n', type=int, help='most similar words', default=30)
parser.add_argument('--fasttext_min_similarity', type=float, help='cosine similarity ', default=0.80)
parser.add_argument('--edit_distance_threshold', type=int, help='edit distance ', default=3)
args = parser.parse_args()

filename_read = args.data
similar_n = args.similar_n
fasttext_min_similarity = args.fasttext_min_similarity
edit_distance_threshold = args.edit_distance_threshold


import utils.preprocessing
from gensim.models import FastText
from pyxdameraulevenshtein import damerau_levenshtein_distance

import collections
import numpy as np
import pandas as pd
import re
from keras.preprocessing.text import text_to_word_sequence

import warnings
warnings.filterwarnings("ignore")

## Data read
df = pd.read_csv("data/"+str(filename_read), encoding = "CP949")
df = utils.preprocessing.Preprocessing().organ_result(df)

def organ_extract(df):
    
    temp=[]
    
    for _ in range(len(df)):
        
        if ':' in df.iat[_][0]:
            temp.append(df.iat[_][0].split(":")[1].strip())
        if ';' in df.iat[_][0]:
            temp.append(df.iat[_][0].split(";")[1].strip())
            
    return temp

organ_list = organ_extract(df["organ_result"])
organ_list = [x for x in organ_list if x]

stop_words=["ss","spp","ssp","mrsa","mssa","group"]

## Extraction of data using regular expression

organ_word=[]
for _ in range(len(organ_list)):
    
    temp_words = text_to_word_sequence(organ_list[_]) #Tokenizer
    
    for _ in temp_words:
        if _ not in stop_words:
            if len(_)>3:
                organ_word.append(_)

organ_corpus = sorted(list(set(organ_word)))
print("Organism count: " + str(len(organ_corpus)))

## Misspelling Detection
print("---Misspelling Detection---")

dict_corpus=list(pd.read_csv("data/misspelling_detection.txt", header=None)[0])
misspell=sorted(list(set(organ_word)))
for _ in dict_corpus:
    if _ in misspell: 
        misspell.remove(_)

vocab_m={}
for _ in misspell:
    vocab_m[_]=organ_word.count(_)
print("Misspell count: " + str(len(vocab_m)))

vocab_c=collections.Counter(organ_word)
for _ in misspell:
    del vocab_c[_]
print("Correct count: " + str(len(vocab_c)))

## Load BioWordVec
print("### Caution: take a long time ###")
print("BioWordVec loading")
bio_model = FastText.load_fasttext_format('./pretrained/BioWordVec_PubMed_MIMICIII_d200.bin')
print("BioWordVec loaded")

## Candidate Generation
print("---Candidate Generation---")

nonalphabetic = re.compile(r'[^a-zA-Z]')

def include_spell_mistake(word, similar_word, score):
    
    return (score > fasttext_min_similarity 
            and damerau_levenshtein_distance(word, similar_word) <= edit_distance_threshold
            and len(similar_word) > 3
            and word[0] == similar_word[0]
            and nonalphabetic.search(similar_word) is None)

## Candidate Ranking
print("---Candidate Ranking---")

# Grid Search
restrict_vocab_size = np.arange(100000,1000000,100000)
rank=1

word_to_mistakes = collections.defaultdict(list)
for word, freq in vocab_m.items():
        
    if len(word) <= 3 or nonalphabetic.search(word) is not None:
        continue
    
    for i in range(len(restrict_vocab_size)):
        similar_pre = bio_model.wv.most_similar(word, topn=similar_n,
                                                restrict_vocab=restrict_vocab_size[i])
    
        for similar_p in similar_pre:
            if include_spell_mistake(word, similar_p[0], similar_p[1]) and len(word_to_mistakes[word])<rank:
                word_to_mistakes[word].append(similar_p[0])
            
print("Spelling correction count: " + str(len(word_to_mistakes)))

## Spelling Correction

temp=[]
for word, mistakes in word_to_mistakes.items():
    for mistake in mistakes:
        
        p_score = bio_model.wv.similarity(word, mistake)
        
        if mistake != word:
            temp.append([word, mistake, p_score])

df=pd.DataFrame(temp, columns=["Misspell","Correct","score"])
df=df.sort_values(["Misspell","score"], ascending=True)
df.to_csv("result.csv", index = False, encoding = "CP949")
print("--- end ---")
