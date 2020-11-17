# Similarity-based-Unsupervised-Spelling-Correction-Using-BioWordVec

This is similarity-based unsupervised spelling correction using [BioWordVec] for bacteria culture and antimicrobial susceptibility reports.  
Please visit the original repo of [BioWordVec] (Yijia Zhang, et al.) for more information about the pre-trained BioWordVec.  

## Environments
	python 3
	re
  	pandas
	keras
	gensim 2.3
	pyxDamerauLevenshtein 1.6.1
	
## Pretrained Embedding
* BioWordVec  
https://ftp.ncbi.nlm.nih.gov/pub/lu/Suppl/BioSentVec/BioWordVec_PubMed_MIMICIII_d200.vec.bin

## Usage

Example:  

	python SUSC.py --data sample.csv

Arguments:  

	--data				Data  
	--similar_n			most similar words 
	--fasttext_min_similarity	cosine similarity 
	--edit_distance_threshold	edit distance  


## Overall Architecture
![screensh](./img/architecture.png)

[BioWordVec]: https://github.com/ncbi-nlp/BioWordVec
