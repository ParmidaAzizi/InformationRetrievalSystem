------------------------- Instruction for running the program ------------------------

1. make sure nltk is installed. If not, run: pip install nltk
2. then run the program:
  a. To use the UI with your queries, please run A2_UI.py
  b. To run eval.py, make sure to run it in this exact order: > eval.py query.text qrels.text

---------------------------------------------------------------------------------------
*The following files must be in the same directory: the 6 python files (A2_UI.py Eval.py, Invert_A2.py, Search_A2.py docs_class.py, Installation.py) and porter_stemmer.py

** I used the following formulas to calculate the cosine similarity score: TF-IDF Weight (for both query and documents) = (1 + log(f)) * log(total_documents/df) = tf*idf
Since the weights of terms of the document vector will become zero in the numerator if they are not in the query vector, I decided not to calculate them in the first place. But I still needed them for the normalization done in the denominator. So the code takes advantage of this knowledge and the frequency_dic built in the invert_A2.py and calculates the cosine similarity
of documents.

***The top-k method used is Query Expansion, where query terms with weights more than 2.75 get expanded and their synonyms are added to the original query. This helps to find more relative
documents, not limited to one specific word, but to specific to the meaning of the word.
