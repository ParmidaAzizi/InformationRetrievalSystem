
import copy
from porter_stemmer import PorterStemmer
import re
from collections import Counter
from docs_class import Document_forUse

common_file_path = 'TextFiles/common_words'
docs_file_path = 'TextFiles/cacm.all'
commonWords = []
doc_dic = {}
original_doc_dic = {}

# produce the two output files
def produce_output(f_dictionary,postings):
    with open("dictionary", 'w') as file:
        file.write(f"Term: Frequency\n")
        file.write(f"---------------\n")
        for word, frequency in f_dictionary.items():
            file.write(f"{word}: {frequency}\n")

    with open("postings_list", 'w') as file:
        for word, frequency in postings.items():
            file.write(f"{word}: {frequency}\n")

# extract each field's title and content of every doc in the cacm.all
# and return the list of them
def extract_values(stemming,stopping,commonWords):
    with open(docs_file_path, 'r') as file:
        content = file.read()
    # Use regular expression to find values after each ".I"
    # separating the docs
    pattern = re.compile(r'\.I (\d+)(.*?)(?=\n\.I|\Z)', re.DOTALL)
    output = []
    matches = pattern.findall(content)
    # count = 0
    for match in matches:
        # separate the text following the .I and break them down to their fields
        values = re.findall(r'[\n]*\..\n', match[1])
        values2 = re.split(r'[\n]*\..\n', match[1])
        values2.remove('')
        id= str(match[0])
        temp_titles=[match[0]]
        for i in values:
            temp_titles.append(re.findall(r'[\w\d]+',i))
        titles = list(map(''.join, temp_titles))
        # then put the broken down text into an organized list where it can be used
        res = ["I", titles[0]]
        for i in range(0,len(titles)-2):
            res.append(titles[i+1].lstrip())
            res.append(values2[i].lower().lstrip())
        new_doc = Document_forUse(int(res[1]))
        new_doc2 = Document_forUse(int(res[1]))
        for i in range(2,len(res)):
            if (stemming,stopping):
                if res[i] == "W":
                    new_doc.set_abstractVal(res[i+1])
                    new_doc2.set_abstractVal(res[i+1])
                if res[i] == "T":
                    new_doc.set_title(res[i+1])
                    new_doc2.set_title(res[i+1])
                if res[i] == "A":
                    new_doc.set_author(res[i+1])
                    new_doc2.set_author(res[i+1])
                if res[i] == "B":
                    new_doc.set_publisher(res[i+1])
                    new_doc2.set_publisher(res[i+1])
        new_doc.clean_text()
        if stemming & stopping:
            new_doc.remove_common_words(commonWords)
            new_doc.stem_it()
        elif stemming:
            new_doc.stem_it()
        elif stopping:        
            new_doc.remove_common_words(commonWords)
        doc_dic[int(res[1])] = new_doc
        original_doc_dic[int(res[1])] = new_doc2
    # print(original_doc_dic[2651])
        # output.append(res)
        # count+=1
    return doc_dic, original_doc_dic
   
# stemming the text and returning the new value
def stem_them(document):
    # Create an instance of the PorterStemmer
    stemmer = PorterStemmer()
    processed_document = ''
    current_word = ''
    # for each word in the text, apply stemming
    for char in document:
        if char.isalpha():
            current_word += char.lower()
        else:
            if current_word:
                # Apply stemming to the current word
                stemmed_word = stemmer.stem(current_word, 0, len(current_word) - 1)
                processed_document += stemmed_word
                current_word = ''
            processed_document += char.lower()
    return processed_document

def stem_them_v2(document):
    # Create an instance of the PorterStemmer
    stemmer = PorterStemmer()
    processed_document = ''
    current_word = ''
    words = document.split()
    for current_word in words:
        # print(current_word)
        # Apply stemming to the current word
        stemmed_word = stemmer.stem(current_word, 0, len(current_word) - 1)
        # print("stemmed:", stemmed_word)
        processed_document += stemmed_word
        current_word = ''
        processed_document += " "
    return processed_document

# removing symbols from the strings
def simplify_text(string):
        pattern = re.compile(r'\W+')  
        result_string = re.sub(pattern, ' ', string)
        return result_string



# populates the postings_list
# doc is the current document with stemming and stopword applied to it,
# original_doc is the original current document
# dic is our dictionary
# postings is the dictionary we're populating
def detail_update(doc,original_doc,dic,postings,stemming,stopping):

    # a temporary helper dictionary
    position_list = {}

    # Tokenize the id, title and abstract into words
    doc_id = doc.get_id()
    title_of_doc = doc.get_title().split()
    abstract_of_doc = doc.get_abstractVal().split()

    doc_authors = doc.get_author()
    doc_authors = doc_authors.split('\n')

    filtered_authors = [item for item in doc_authors if item != ""]
    if filtered_authors:
        # filtered_authors = " ".join(filtered_authors)
        for author in filtered_authors:
            name_list2 = simplify_text(author).split()
            filtered_results2 = [item for item in name_list2 if len(item) > 1]
            author_name2 = " ".join(filtered_results2)
            a_name2 =  author_name2.split()
            # print("without stem:",a_name2)
    else:
        a_name2 = []

    # special condition for when stemming is on
    if(stemming):
        temp_org_title = simplify_text(original_doc.get_title())
        org_title = stem_them_v2(temp_org_title)
        org_title_of_doc = org_title.split()

        temp_org_abs = simplify_text(original_doc.get_abstractVal())
        org_abstract = stem_them_v2(temp_org_abs)
        org_abs_of_doc = org_abstract.split()

        doc_authors = doc.get_author()
        doc_authors = doc_authors.split('\n')
        filtered_authors = [item for item in doc_authors if item != ""]
        if filtered_authors:
            # filtered_authors = " ".join(filtered_authors)
            for author in filtered_authors:
                name_list = (simplify_text(author)).split()
                filtered_results = [item for item in name_list if len(item) > 1]
                author_name = " ".join(filtered_results)
                stemmed_name = stem_them_v2(author_name)
                a_name = stemmed_name.split()
                # print("with stem:",a_name)

        else:
            a_name = []


    elif (stopping):
        org_title = simplify_text(original_doc.get_title())
        org_title_of_doc = org_title.split()

        org_abstract = simplify_text(original_doc.get_abstractVal())
        org_abs_of_doc = org_abstract.split()

        doc_authors = doc.get_author()
        doc_authors = doc_authors.split('\n')

        filtered_authors = [item for item in doc_authors if item != ""]
        if filtered_authors:
            # filtered_authors = " ".join(filtered_authors)
            for author in filtered_authors:
                name_list = (simplify_text(author)).split()
                filtered_results = [item for item in name_list if len(item) > 1]
                author_name = " ".join(filtered_results)
                # stemmed_name = stem_them_v2(author_name)
                a_name = author_name.split()
                # print("with stem:",a_name)

        else:
            a_name = []


    # all the terms without repeatition
    all_text = set(title_of_doc + abstract_of_doc)

    authors_dic = {}
    found_a = False


    # two cases of processing terms in the title, if stemming True, or when False
    if(stopping or stemming):
        
        for i in range(0,len(org_title_of_doc)):
            if org_title_of_doc[i] in dic:
                if org_title_of_doc[i] in position_list:
                    position = ["title", i]
                    position_list[org_title_of_doc[i]].append(position)
                else:
                    position_list[org_title_of_doc[i]] = [["title", i]]
    else:
        for i in range(0,len(title_of_doc)):  
            if title_of_doc[i] in dic:
                
                if title_of_doc[i] in position_list:
                    position = ["title", i]
                    position_list[title_of_doc[i]].append(position)
                else:
                    position_list[title_of_doc[i]] = [["title", i]]

    
    # two cases of processing terms in the abstract, if stemming True, or when False
    if not abstract_of_doc == []:
        if(stopping or stemming):
            for i in range(0,len(org_abs_of_doc)):
                if org_abs_of_doc[i] in dic:
                    if org_abs_of_doc[i] in position_list:   
                        position_list[org_abs_of_doc[i]].append(["abstract", i])
                    else:
                        position_list[org_abs_of_doc[i]] = [["abstract", i]]
            
        else:
            for i in range(0,len(abstract_of_doc)):
                if abstract_of_doc[i] in dic:
                    if abstract_of_doc[i] in position_list:          
                        position_list[abstract_of_doc[i]].append(["abstract", i])
                    else:
                        position_list[abstract_of_doc[i]] = [["abstract", i]]

        
    if (stemming or stopping):
        for author in a_name:
            if author in position_list:
                position_list[author].append(["author",0])
            elif author in authors_dic:
                found_a = True
                authors_dic[author].append(["author",0])
            else:
                found_a = True
                authors_dic[author] = ["author",0]
    else:
        for author in a_name2:
                if author in position_list:
                    position_list[author].append(["author",0])
                elif author in authors_dic:
                    found_a = True
                    authors_dic[author].append(["author",0])
                else:
                    found_a = True
                    authors_dic[author] = ["author",0]
            
    # add the gathered inpormation for this doc and add it to
    # each present term's posting_list
    for word in all_text:
        if word in postings:
          
            postings[word][doc_id] = [len(position_list[word]),position_list[word]]
    if found_a:
        for name,pos in authors_dic.items():
            # print(name)
            if name not in postings:
                postings[name] = {}
            postings[name][doc_id] = [20,""]
            



def make_dictionary(f_dictionary,postings):
    for key, value in postings.items():
        f_dictionary[key] = len(value)


def create_word_dictionary(strings):
    # Remove punctuation and convert to lowercase
        # Combine all strings into a single string
    text = ' '.join(strings)
    words = text.split()
    # print("words:",words)
    expanded_words = [] 
    for word in words:
        if '-' in word:
            expanded_words.extend(split_hyphenated_word(word))
        else:
            expanded_words.append(word)
    # print("expanded_words:",expanded_words)
    text=" ".join(expanded_words)

    # Split the combined text into words
    text = simplify_text(text)
    # print(text)
    text = re.sub(r'[^\w\d\s]', '', text.lower())
    # print("after ",text)
    
    # Split the text into words
    words = text.split()
    # print("after split:",words)
    for word in words:
        word = word.lower()

    # Use set to get unique words
    word_set = set(words)

    # Convert the set to a dictionary with values set to None
    word_dictionary = {word: [] for word in word_set}

    return word_dictionary

# input is a list all the string in all the docs, make a list of words out of the
# strings and count their frequencies
def count_word(strings,f_dictionary):
    # Combine all strings into a single string
    combined_text = ' '.join(strings)
    # Split the combined text into words
    combined_text = simplify_text(combined_text)
    words = combined_text.split()
    
    for word in words:
        word = word.lower()
    words = (''.join(filter(str.isalpha, word)) for word in words)
    # counting the frequency of each word
    word_frequency = Counter(words)
    updated_word_frequency = {key: value for key, value in word_frequency.items() if key != "" and (key in f_dictionary)}  
    return updated_word_frequency

def build_frequency_dictionary(doc_dic,f_dictionary):
    result = {}
    for docID, doc in doc_dic.items():
        full_string = []
        full_string.append(doc.get_title())
        full_string.append(doc.get_abstractVal())
        freq = count_word(full_string,f_dictionary)
        # count the frequency of all the terms in .T and .W
        result[docID] = freq
    return result
    

def split_hyphenated_word(word):
    # Split a hyphenated word into three parts
    parts = word.split('-')
    return [word.replace("-", "")] + parts

def add_authors(filtered_postings, original_doc_dic):
    filtered_postings["costum_made_authors"] = {}
    for docID, docum in original_doc_dic.items():

        doc_authors = docum.get_author()
        doc_authors = doc_authors.split('\n')

        filtered_authors = [item for item in doc_authors if item != ""]
        if filtered_authors:
            
            for author in filtered_authors:
                if author in filtered_postings["costum_made_authors"]:
                    filtered_postings["costum_made_authors"][author].append(docID)
                else:
                    filtered_postings["costum_made_authors"][author] = [docID]
    return filtered_postings

def inverted_main_for_UI(stemming,stopping):

    if stopping:
        with open(common_file_path, 'r') as file:
            for line in file:
                commonWords.append(line.replace("\n", ""))
    
    # read the docs and make a codument instance for each. the instances are held
    #  in doc_dic and original_doc_dic
    doc_dic, original_doc_dic = extract_values(stemming,stopping,commonWords)


    # ----------------------------------
    # calculate the first part of the dictionary
    # ----------------------------------
    full_string = []
    # gather the fields where the search will be happening in: .T and .W
    for key, doc in doc_dic.items():
        full_string.append(doc.get_title())
        full_string.append(doc.get_abstractVal())


    # count the frequency of all the terms in .T and .W
    result = create_word_dictionary(full_string)

    # sort the dictionary on an alphabetic order
    f_dictionary = dict(sorted(result.items()))
    if "" in f_dictionary:

        del f_dictionary[""]


    # ----------------------------------
    # calculate the postings_list
    # ----------------------------------
    # temp_org_docs_dcc used in populating posting_list
    temp_org_docs_dic = copy.deepcopy(original_doc_dic)

    # detail_dic holds temporary details of postings for each doc
    # the actual data collected for the posting_list
    detail_dic = f_dictionary
    postings = {}
    for key,value in f_dictionary.items():
        postings[key] = {}

    # calculate information and populate posting_list
    for i in range(1,len(doc_dic)+1):
        # the main function for populating postings
        detail_update(doc_dic[i],temp_org_docs_dic[i],detail_dic,postings,stemming,stopping)


    # ----------------------------------
    # calculate the second part of the dictionary
    # ----------------------------------
    final_postings = {}

    filtered_postings = {key: value for key, value in postings.items() if value}

    filtered_postings_with_authors = add_authors(filtered_postings, original_doc_dic)

    # Sort the filtered_postings based on the df
    for key, inner_dict in filtered_postings_with_authors.items():
        sorted_inner_dict = dict(sorted(inner_dict.items(), key=lambda x: x[1][0], reverse=True))
        final_postings[key] = sorted_inner_dict
        make_dictionary(f_dictionary,filtered_postings_with_authors)

    # ----------------------------------
    # outputs
    # ----------------------------------
    # produce two files called: "dictionary" and "postings_list"
    produce_output(f_dictionary,final_postings)

    frequency_dic = build_frequency_dictionary(doc_dic,f_dictionary)
    # return these values to test.py
    return(original_doc_dic,doc_dic,frequency_dic,f_dictionary,final_postings)
