# -*- coding: utf-8 -*-

"""

@ author: Taehyeong Kim
@ e-mail: taehyeong93@korea.ac.kr

"""


import pandas as pd
import re
from keras.preprocessing.text import text_to_word_sequence


class SNOMED:
    
    def __init__(self):
        print("--- SNOMED ---")
        
    def SNOMED_dictionary(self):
        
        # SNOMED Dictionary
        snomed=pd.read_csv("data/SNOMED.csv")
        snomed_series=snomed["concept_name"].dropna()
        snomed_list=list(snomed_series.unique())
        snomed_list=[x for x in snomed_list if x]

        dict_word=[]
        for _ in range(len(snomed_list)):

            temp_words = text_to_word_sequence(snomed_list[_]) #Tokenizer

            for _ in temp_words:
                if len(_)>1:
                    result = re.sub('[^a-zA-Z]', '', _)
                    dict_word.append(result)

        # Generate Dictionary
        with open('data/SNOMED_dictionary.txt', 'w') as f:
            for item in dict_word:
                f.write("%s\n" % item)

        dict_corpus = sorted(list(set(dict_word)))
        dict_corpus = [x for x in dict_corpus if x]
        print("Corpus count:" + str(len(dict_corpus)))
        
        # Generate Corpus
        with open('data/misspelling_detection.txt', 'w') as f:
            for item in dict_corpus:
                f.write("%s\n" % item)
