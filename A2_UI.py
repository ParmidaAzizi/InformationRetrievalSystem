from invert_A2 import *
from search_A2 import *
from docs_class import *
import time
import installation
installation
from nltk.corpus import wordnet

if __name__ == "__main__":

    total_time = 0
    iteration_count = 0

    print("You are now runnin the IR System of 842A2.\n")
    # Default value for stemming and stopword
    stemming = False
    stopping = False

    # Ask the user if they want stemming
    user_input = input("Do you want stemming enabled for your searches? (yes/no): ").lower()
    # Check if the user's input is affirmative
    if user_input == 'yes' or user_input == 'y':
        stemming = True
        print("Stemming is enabled.")
    else:
        print("Stemming is not enabled.")

    # Ask the user wants stopword to be active
    user_input = input("Do you want to remove common words from your searches? (yes/no): ").lower()
    # Check if the user's input is affirmative
    if user_input == 'yes' or user_input == 'y':
        stopping = True
        print("StopWord is enabled.")
    else:
        print("StopWord is not enabled.")
    
    original_docs_dic, doc_dic, frequency_dic, dictionary, postings = inverted_main_for_UI(stemming,stopping)

    while True:

        print("")
        user_input = input("Enter a phrase to be searched (type 'ZZEND' to quit): ")
        
        if user_input.upper() == "ZZEND":
            # Calculate and display the average time
            average_time = total_time / iteration_count if iteration_count > 0 else 0
            print("-------------------------------------------------------")
            print("Exiting the app.")
            print(f"Average time per iteration: {average_time:.4f} seconds")
            print("-------------------------------------------------------")
            break
            
        start_time = time.time()
        
        sorted_docs = search_main_for_UI(original_docs_dic, doc_dic, frequency_dic, dictionary, postings, [user_input,[]], stemming, stopping)
        
        end_time = time.time()
        time_interval = end_time - start_time

        print()
        print("---------------------------------------")


        k = 50
        print("Value of 'K' is set to 50.")

        if (len(sorted_docs)>k-1):
            max_range = k
        else:
            max_range = len(sorted_docs)


        if max_range == 0:
            print("---------------------------------------")
            print("----       no matches found        ----")
            print("---------------------------------------")

        else:
            if max_range < 10:
                print("---------------------------------------")
                print("Not many results found for your search")
                print("---------------Results-----------------")

            else:
                print("---------------Results-----------------")
            for i in range(0,max_range):
                if i>0:
                    print("------------")
                print(f"Rank #{i+1}:")
                found_doc = original_docs_dic[sorted_docs[i][0]]
                print(f"Score: %.4f" % sorted_docs[i][1])

                print(f"DocID:{found_doc.get_id()}")
                title = found_doc.get_title()
                author = found_doc.get_author()
                print(f"Title: {title.title()}")
                print(f"Author(s): {author.title()}")
            print("----------------------------------------")
            print(f"Search time: {round(time_interval, 3)}s")
            print("----------------------------------------")

            total_time = total_time + time_interval
            iteration_count += 1