import sys
from invert_A2 import *
from search_A2 import *
import time
import installation
installation
from nltk.corpus import wordnet


def read_query(file1_path):
    # Open and read the file
    with open(file1_path, "r") as file:
        lines = file.readlines()

    info = {}
    # Process each line
    collectingW = False
    collectingA = False
    query = ""
    author = ""
    N_value = ""
    for line in lines:
        line = line.strip()
        line_list = line.split()
        if len(line_list)==2 and line_list[0]==".I":
            id = line_list[1]
            query = ""
            author = ""
            # N_value = ""
        elif len(line_list)==1 and line_list[0]==".W":
            collectingW = True
            # collectingN = False
            collectingA = False
        elif len(line_list)==1 and line_list[0]==".A":
            collectingW = False
            # collectingN = False
            collectingA = True
        elif len(line_list)==1 and line_list[0]==".N":
            # collectingN = True
            collectingA = False
            collectingW = False
        elif (len(line_list)==0):
            info[id] = [query.lstrip(),author.lstrip()]
            # info[id] = query.lstrip()
        elif(collectingW):
            query = query + " "+ ' '.join(line_list)
        elif(collectingA):
            author = author + "-- "+ ' '.join(line_list)
        # elif(collectingN):
        #     N_value = N_value + " "+ ' '.join(line_list)

    return info


def read_qrels(file2_path):
    # Open and read the file
    with open(file2_path, "r") as file:
        lines = file.readlines()

    # To store the grouped data
    grouped_data = {}

    # Process each line
    for line in lines:
        # Split the line into individual values
        values = line.strip().split()

        # Extract the group key (the first value) and the second value
        group_key = int(values[0])  # Convert the group key to an integer
        second_value = int(values[1])  # Convert the second value to an integer

        # Check if the group key is already in the dictionary
        if group_key in grouped_data:
            # If it is, append the second value to the existing list
            grouped_data[group_key].append(second_value)
        else:
            # If it's not, create a new list with the second value
            grouped_data[group_key] = [second_value]

    return grouped_data


def find_matching_document_ids(doc_ids_list, doc_scores_list):
    # Initialize a list to store the indices of matching document IDs
    matching_indices = []

    # Iterate through document IDs in the first list
    for doc_id in doc_ids_list:
        # Check if the document ID is present in the second list
        for i, item in enumerate(doc_scores_list):
            if doc_id == item[0]:
                matching_indices.append(i)

    return matching_indices

def sum_list(numbers):
    total_sum = 0
    for num in numbers:
        total_sum += num
    return total_sum



if __name__ == "__main__":
    # Check if two files are provided as arguments
    if len(sys.argv) != 3:
        print("Usage: python eval.py TextFiles/query.text TextFiles/qrels.text")
        sys.exit(1)

    # Get command-line arguments
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]

    stemming = False
    stopping = False

    sum_ap = 0
    sum_rp = 0
    counting = 0

    top_k = 50
    # Ask the user if they want stemming
    user_input = input("Do you want stemming enabled for your searches? (yes/no): ").lower()

    if user_input == 'yes' or user_input == 'y':
        stemming = True
        print("Stemming is enabled.")
    else:
        print("Stemming is not enabled.")

    # Ask the user wants stopword to be active
    user_input = input("Do you want to remove common words from your searches? (yes/no): ").lower()

    if user_input == 'yes' or user_input == 'y':
        stopping = True
        print("StopWord is enabled.")

    else:
        print("StopWord is not enabled.")
    
    original_docs_dic, doc_dic, frequency_dic, dictionary, postings = inverted_main_for_UI(stemming,stopping)
    print(f"---------------------------")

    print("stem:",stemming)
    print("stop:",stopping)
    print(f"K value is set to {top_k}")
    try:
        # Open and read the contents of the first file
        queries= read_query(file1_path)
        
        # Open and read the contents of the second file
        relevant_docs = read_qrels(file2_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        exit

    start_time = time.time()
    for query_number,relv_docs in relevant_docs.items():
        counting += 1
        query = queries[str(query_number)]

        sorted_docs = search_main_for_UI(original_docs_dic, doc_dic, frequency_dic, dictionary, postings, query, stemming, stopping)
        docs_returned = sorted_docs[:top_k]
        positions_of_relev_docs_returned = find_matching_document_ids(relv_docs,docs_returned)
        print(f"-----------")
        if len(positions_of_relev_docs_returned)>0:
            positions_of_relev_docs_returned = sorted(positions_of_relev_docs_returned)
            count = 0
            list_of_precisions = []
            for i in positions_of_relev_docs_returned:
                count += 1
                precision = count/(i+1)
                list_of_precisions.append(precision)

            sum_of_pre = sum_list(list_of_precisions)
            ap = sum_of_pre/(len(relv_docs))
            sum_ap = sum_ap + ap
            r = len(positions_of_relev_docs_returned)
            closest_index = max((i for i, x in enumerate(positions_of_relev_docs_returned) if x < r), default=None)
            if (closest_index==None):
               number_of_rel_in_top_r = 0
            else:
                number_of_rel_in_top_r = closest_index + 1
            r_precision = number_of_rel_in_top_r/r
            sum_rp = sum_rp + r_precision
        else:
            ap = 0.0
            r_precision = 0.0
        print(f"for query #{query_number}, got {len(positions_of_relev_docs_returned)} out of {len(relv_docs)} relevant docs. | AP: {round(ap, 2)} | R-precision: {round(r_precision, 2)}")
    
    end_time = time.time()
    print(f"-----------")
    print(f"Average time per query: {(end_time-start_time)/counting}")
    print(f"Final MAP: {round((sum_ap/counting), 4)}")
    print(f"Final Average R-precision: {round((sum_rp/counting), 4)}")
    

        

