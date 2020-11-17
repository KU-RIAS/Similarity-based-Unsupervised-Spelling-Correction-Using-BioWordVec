# -*- coding: utf-8 -*-

"""

@ author: Taehyeong Kim
@ e-mail: taehyeong93@korea.ac.kr

"""


import pandas as pd
import re


class Preprocessing:
    
    def __init__(self):
        print("--- Preprocessing ---")
        
    def organ_result(self, df):
        
        # Missing Value Remove
        df = df.dropna()
        
        # Lowercase
        df["result"] = df.result.apply(lambda x : x.lower())
        
        # Organism Check
        df["organ_count"] = df.result.apply(lambda x : 1 if "organism" in x else 0)
        organ_df = df.loc[df['organ_count'] != 0]
        organ_df = organ_df.drop(["organ_count"], axis=1)
        
        # Organ Extraction
        
        organ_list = []
        
        organ_df_result = (i for i in organ_df['result'])
        
        for _ in range(len(organ_df)):
            
            text = next(organ_df_result)
            
            if "\r" in text:
                split_text = text.split("\r\n")
            else:
                split_text = text.split("\n")
            
            split_text = [i.strip() for i in split_text if len(i) >= 1]
            
            organ_index = []
            organ_result = []
            
            for sentence_index, sentence in enumerate(split_text):
                
                if ("organ" in sentence):
                    organ_index.append(sentence_index)
                    
            for index_value in range(1, len(organ_index)+1):
                
                if (index_value != len(organ_index)):
                    organ_text = split_text[organ_index[index_value-1] : organ_index[index_value]]
                    organ_text, colony_amount_text = self.reorgan(organ_text)
                    if len(organ_text) > 1:
                        organ_result.append(organ_text+colony_amount_text)
                        
                elif (index_value == len(organ_index)):
                    organ_text = split_text[organ_index[index_value-1] : ]
                    organ_text, colony_amount_text = self.reorgan(organ_text)
                    if len(organ_text) > 1:
                        organ_result.append(organ_text+colony_amount_text)
                        
            organ_list.append(organ_result)
            
        temp_df = pd.DataFrame(organ_list)
        
        # Organ Reconstruction
        
        temp_df.index = organ_df.index

        temp_series=[]

        for _ in range(len(temp_df.columns)):
            
            temp_series.append(temp_df[_].dropna())
            
        temp_df = pd.DataFrame(pd.concat(temp_series))
        
        temp_df.rename(columns={0:'organ_result'}, inplace=True)
        
        df = organ_df.join(temp_df, how='inner')
        
        # remove hangul at organ_result
        df = self.remove_hangul(df)
        
        return df
        
        
    def reorgan(self, organ_text):
        
        text_index = []
        colony_amount_index = []
        
        reorgan_text = []
        colony_amount_text = []
        
        for count_index, organ_text_element in enumerate(organ_text):
            
            split_organ_text_element = organ_text_element.split()
            
            for index, value in enumerate(split_organ_text_element):
                
                if (value == 'colony') or (value == 'amount'):
                    colony_amount_index.append(count_index)
                    break
                    
                elif (value == "s") or (value == "i") or (value == "r"):
                    if index < 5: # high level gm resistance, high level sm resistance
                        if len(split_organ_text_element) < 9 :
                            text_index.append(count_index)
                            break
                        
                elif value == 'esbl':
                    if ('+' in split_organ_text_element) or ('-' in split_organ_text_element) or ('pos' in split_organ_text_element) or ('neg' in split_organ_text_element):
                        if len(split_organ_text_element) < 9 :
                            text_index.append(count_index)
                            break
                        
            # s       i       r / s        i        r
            if ('s' in split_organ_text_element) and ('r' in split_organ_text_element) and ('i' in split_organ_text_element):
                text_index.remove(count_index)
                
        text_index.insert(0,0)
        text_index = list(set(text_index))
        
        for _ in text_index:
            reorgan_text.append(organ_text[_])
            
        for _ in colony_amount_index:
            colony_amount_text.append(organ_text[_])
            
        return reorgan_text, colony_amount_text
        
        
    def remove_hangul(self, df):
        
        hangul = re.compile('[ㄱ-ㅣ가-힣]+')
        
        for i in range(len(df["organ_result"])):
            for j in range(len(df["organ_result"].iat[i])):
                hangul_result = hangul.findall(df["organ_result"].iat[i][j])
                                
                if len(hangul_result)>0:
                    for m in hangul_result:
                        df["organ_result"].iat[i][j] = df["organ_result"].iat[i][j].replace(m,'')
                    
        return df
