import time
import copy
from math import *
from porter_stemmer import PorterStemmer
import re
from collections import defaultdict, Counter
from docs_class import Document_forUse
from invert_A2 import *
from nltk.corpus import wordnet


common_file_path = 'TextFiles/common_words'
idf_values = {}
original_docs_dic={} 
doc_dic = {}
dictionary ={}
postings ={}
stemming = False
stopping = False

# improving the query:
# -------------------------
def split_hyphenated_word(word):
    # Split a hyphenated word into three parts
    parts = word.split('-')
    return [word.replace("-", "")] + parts

def expand_query_term(term):
        "Gets synonyms"
        synonyms = []
        for syn in wordnet.synsets(term):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        return synonyms

# -------------------------

# freqInDoc from postings
def highlight_word(word, context, stemming):
    # the dark red color code for highlighting the word
    highlight_start = '\033[31m'
    highlight_end = '\033[0m'     

    if stemming:
        pattern = re.compile(rf'\b{re.escape(word)}\w*', re.IGNORECASE)
    else:
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)

    # Define a function to replace the matches with the highlighted version
    def highlight(match):
        return f'{highlight_start}{match.group()}{highlight_end}'

    highlighted_context = pattern.sub(highlight, context)

    return highlighted_context


# Run invert.py and process the dictionary and the posting_list
# original_docs_dic, stemming, stopping, dictionary, postings = inverted_main()


def get_df(dictionary, term):
    df = dictionary[term]
    # df from dictionary
    return df

def get_idf(dictionary, term):
    df = get_df(dictionary, term)
    num = len(original_docs_dic)
    idf = log((num/df),10)

    return idf

# rerm frequency
def tF(freq):
    return (1+log(freq,10))

def get_weight(frequencyInDoc,idf):
    term_frequency = tF(frequencyInDoc)
    w = (term_frequency*idf)
    return w
    # w = tf * idf

# get all the terms in the query, make it a vector
# each doc that has at least one of the terms will be assigned a vector or the same size
# if more than one term in a doc, the doc's vetor will be updated
# after all docvectors calculated, calculate cosine similarity
def get_norm_of(vector):
    sum = 0
    for term,value in vector.items():
        sum = sum + pow(vector[term],2)
    return sqrt(sum)

def get_queryTimesDoc(query,doc):
    sum = 0
    for term,value in query.items():
        sum = sum + (query[term]*doc[term])

    return sum

def calculate_cosine_sim(docs_vector_list,query_term_vector):
    list_of_doc_and_scores = []
    for doc,doc_vector in docs_vector_list.items():
        numerator = get_queryTimesDoc(query_term_vector,doc_vector)
        nor_doc = get_normalized(doc, frequency_dic)
        query_norm = get_norm_of(query_term_vector)
        denominator = (nor_doc * query_norm)
        list_of_doc_and_scores.append([doc,(numerator / denominator)])
    return list_of_doc_and_scores
    
def find_weight_vector_of_query(query_term_frequency_vector):
    temp_vector = {}
    for term,frequency in query_term_frequency_vector.items():
        term_idf = idf_values[term]
        weight = get_weight(frequency,term_idf)
        temp_vector[term] = weight
    return temp_vector


def get_normalized(document_id, frequency_dic):
    temp_vector = {}
    freq = frequency_dic[document_id]
    for term,frequency in freq.items():
        term_idf = get_idf(dictionary,term)
        weight = get_weight(frequency,term_idf)
        temp_vector[term] = weight
    norm_of_doc = get_norm_of(temp_vector)
    return norm_of_doc
       
def find_weight_vector_of_docs(document_id,query_term_vector):
    temp_vector = {}
    for term,value in query_term_vector.items():
        term_idf = idf_values[term]
        positionsInfo = postings[term]
        if document_id in positionsInfo:
            frequencyInDoc = positionsInfo[document_id][0]
            weight = get_weight(frequencyInDoc,term_idf)
            temp_vector[term] = weight
        else:
            temp_vector[term] = 0
    return temp_vector


def search_main_for_UI(org_docs_dic, doc_d, freq_dic, dic, pstngs, input1, stem, stop):
    have_authors = False
    global original_docs_dic 
    global postings 
    global stemming
    global stopping
    global frequency_dic 
    global dictionary 
    global doc_dic
    original_docs_dic = org_docs_dic
    doc_dic = doc_d
    dictionary = dic
    frequency_dic = freq_dic
    stemming = stem
    stopping = stop
    postings = pstngs

    user_input = input1[0] #the actual query sting
    authors = input1[1] # the author names provided with the query

    # reading the author field, if provided.
    # docs_with_rel_authors hold the authors' name for this query
    docs_with_rel_authors = []
    if len(authors)>0:
        # have_authors = True
        names = authors.split('-- ')

        filtered_names = [item for item in names if item != ""]
        # print(filtered_names)
        for name in filtered_names:
            for k,v in postings['costum_made_authors'].items():
                if (name.lower()) in k:
                    # print("name: ",name,"in: ",v)
                    for doc_id in v:
                        if doc_id not in docs_with_rel_authors:
                            docs_with_rel_authors.append(doc_id)

    # ---------------------------
    #   processing the query
    # ---------------------------
    user_input = user_input.lower()
    user_input = simplify_text(user_input)
    input_list1 = user_input.split()
    for_expansion = []
    user_input2 = []
    returningword = []
    for word in input_list1:
        returningword.append(word.replace("\n", ""))

    if stemming:
        for i in returningword:
            stemmer = PorterStemmer()
            user_input2.append(stemmer.stem(i, 0, len(i) - 1))
            for_expansion.append([i,stemmer.stem(i, 0, len(i) - 1)])
    else:
        user_input2 = returningword

    if stopping:
        with open(common_file_path, 'r') as file:
            for line in file:
                commonWords.append(line.replace("\n", ""))
        user_input2 = [word for word in user_input2 if word.lower() not in commonWords]

    user_input_filtered = []


    # ---------------------------------------------------------
    # Make the query vector from query
    # ---------------------------------------------------------
    # only if the query is more than one word, remove the terms
    # with a very low idf
    if len(user_input2)>0:
        for term in user_input2:
            if term in  postings:
                # term_idf = get_idf(term)
                term_idf = get_idf(dictionary, term)
                idf_values[term] = term_idf
                user_input_filtered.append(term)

    query_term_vector_f = {}
    for word in user_input_filtered:
        if word in postings:
            # print(word)
            if word in query_term_vector_f:
                query_term_vector_f[word] += 1
            else:
                query_term_vector_f[word] = 1
    
    query_term_vector = find_weight_vector_of_query(query_term_vector_f)
    to_be_extended = []
    for term_on_q, weight_of_term in query_term_vector.items():
        # print(term_on_q, ": ", weight_of_term)
        if weight_of_term > 2.75:
            if stemming:
                for i in for_expansion:
                    if i[1] == term_on_q:
                        to_be_extended.append(i[0])
            else:
                to_be_extended.append(term_on_q)
    # print("to be extended:")
    
    new_list_x = []

    for x in to_be_extended:
        temp_list = []
        # print(x)
        list_x = expand_query_term(x)
        # print(list_x)
        if stemming:
            for i in list_x:
                stemmer = PorterStemmer()
                temp_list.append(stemmer.stem(i, 0, len(i) - 1))
                #for_expansion.append([i,stemmer.stem(i, 0, len(i) - 1)])
            if stopping:
                with open(common_file_path, 'r') as file:
                    for line in file:
                        commonWords.append(line.replace("\n", ""))
                new_list_x = new_list_x + [word for word in user_input2 if word.lower() not in temp_list]
            else:
                new_list_x = new_list_x + temp_list
        else:
            if stopping:
                with open(common_file_path, 'r') as file:
                    for line in file:
                        commonWords.append(line.replace("\n", ""))
                new_list_x = new_list_x + [word for word in user_input2 if word.lower() not in list_x]
            else:
                new_list_x = new_list_x + list_x

    new_list_x = new_list_x + user_input_filtered
    final_query_list = list(set(new_list_x))
    final_query_vect = {}
    for word in final_query_list:
        if word in postings:
            if word not in idf_values:
                # term_idf = get_idf(term)
                term_idf = get_idf(dictionary, word)
                idf_values[word] = term_idf
            # print(word)
            if word in final_query_vect:
                final_query_vect[word] += 1
            else:
                final_query_vect[word] = 1
    
    query_term_vector_final = find_weight_vector_of_query(final_query_vect)
    # print("all extended:")
    # print(list(set(new_list_x)))
    # --------------------------------
    # find the document vectors, but to make the
    # computation less, only find the words from the query vector
    # because either way, the other terms from
    # the query will be zero for the doc
    # But for normalization, we need all the terms in the doc and
    # that is computed separately using the frequency dictionary built in
    # invert_A2.py
    # ---------------------------------

    docs_vector_list = {}
    for term in query_term_vector_final:
        for kTerm,vPositions in postings.items():
            if kTerm == term:
                for document_id,document_info in vPositions.items():
                    # only if this document hasn't been processed before, calculate its vector
                    # and add it to the docs_vector_list
                    if document_id not in docs_vector_list:
                        weight_vector_of_doc = find_weight_vector_of_docs(document_id,query_term_vector_final)
                        docs_vector_list[document_id] = weight_vector_of_doc
                       

    doc_list_with_scores = calculate_cosine_sim(docs_vector_list,query_term_vector_final)
    sorted_docs = sorted(doc_list_with_scores, key=lambda x: x[1], reverse=True)
    for pairA in docs_with_rel_authors:
        found = False
        # Check if the first item of pairA is already in sorted_docs
        for i, pairB in enumerate(sorted_docs):
            if pairA == pairB[0]:
                # If found, update the second item to "twice"
                sorted_docs[i] = [pairB[0], 0.98]
                found = True
                break
        
        # If not found, add the pairA to sorted_docs
        if not found:
            sorted_docs.append([pairA,0.85])
        
    sorted_docs = sorted(sorted_docs, key=lambda x: x[1], reverse=True)
    
    return sorted_docs
    



