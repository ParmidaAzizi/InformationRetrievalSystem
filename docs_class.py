import re
from porter_stemmer import PorterStemmer

class Document_forUse:
    def __init__(self, document_id, title="", abstract="", publisher="", author="" ):
        self.set_id(document_id)
        self.set_title(title)
        self.set_abstractVal(abstract)
        self.set_publisher(publisher)
        self.set_author(author)

    def set_id(self, document_id):
        if not isinstance(document_id, int):
            raise ValueError("ID must be an integer.")
        self._id = document_id

    def get_id(self):
        return self._id
    
    def set_publisher(self, publisher):
        self._publisher = publisher

    def set_author(self, author):
        self._author = author

    def get_publisher(self):
        return self._publisher

    def get_author(self):
        return self._author
    
    def set_title(self, title):
        if not isinstance(title, str):
            raise ValueError("Title must be a string.")
        self._title = title

    def get_title(self):
        return self._title

    def set_abstractVal(self, abstract):
        if not isinstance(abstract, str):
            raise ValueError("Abstract must be a string.")
        self._abstract = abstract

    def get_abstractVal(self):
        return self._abstract
    
    # remove symbols from title and abstract
    def clean_text(self):
        self.remove_symb_title()
        self.remove_symb_abst()

    def remove_symb_title(self):
        # Define a regular expression pattern to match symbols
        pattern = re.compile(r'\W+')  # \W matches any non-alphanumeric character, and _ matches underscore
        # Use the sub() method to replace matches with an empty string
        string = self.get_title()
        # result_string = re.split(r'\W+', string.strip())
        result_string = re.sub(pattern, ' ', string)
        self.set_title(result_string)
    
    def remove_symb_abst(self):
        # Define a regular expression pattern to match symbols
        pattern = re.compile(r'\W+')  # \W matches any non-alphanumeric character, and _ matches underscore
        # Use the sub() method to replace matches with an empty string
        string = self.get_abstractVal()
        # result_string = re.split(r'\W+', string.strip())
        result_string = re.sub(pattern, ' ', string)
        self.set_abstractVal(result_string)


    # remove common words from title and abstract
    def remove_common_words(self,commonWords):
        self.remove_cw_abstract(commonWords)
        self.remove_cw_title(commonWords)
    
    def remove_cw_abstract(self,commonWords):
        returningword = []
        words = self.get_abstractVal().split()
        for word in words:
            returningword.append(word.replace("\n", ""))
        words_without_common = [word for word in returningword if word.lower() not in commonWords]
        self.set_abstractVal(' '.join(words_without_common))

    def remove_cw_title(self,commonWords):
        returningword = []
        words = self.get_title().split()
        for word in words:
            returningword.append(word.replace("\n", ""))
        words_without_common = [word for word in returningword if word.lower() not in commonWords]
        self.set_title(' '.join(words_without_common))

    # stem the title and abstract
    def stem_it(self):
        self.stem_title_v2()
        self.stem_abstract_v2()


    def stem_title_v2(self):
        # Create an instance of the PorterStemmer
        stemmer = PorterStemmer()
        processed_document = ''
        current_word = ''
        document= self.get_title()
        words = document.split()
        for current_word in words:
            # print(current_word)
            # Apply stemming to the current word
            stemmed_word = stemmer.stem(current_word, 0, len(current_word) - 1)
            # print("stemmed:", stemmed_word)
            processed_document += stemmed_word
            current_word = ''
            processed_document += " "
        self.set_title(processed_document)

    def stem_title(self):
        stemmer = PorterStemmer()
        processed_document = ''
        current_word = ''
        document_title = self.get_title()
        for char in document_title:
            if char.isalpha():
                current_word += char.lower()
            else:
                if current_word:
                    # Apply stemming to the current word
                    stemmed_word = stemmer.stem(current_word, 0, len(current_word) - 1)
                    processed_document += stemmed_word
                    current_word = ''
                processed_document += char.lower()
        self.set_title(processed_document)

    def stem_abstract_v2(self):
        # Create an instance of the PorterStemmer
        stemmer = PorterStemmer()
        processed_document = ''
        current_word = ''
        document= self.get_abstractVal()
        words = document.split()
        for current_word in words:
            # print(current_word)
            # Apply stemming to the current word
            stemmed_word = stemmer.stem(current_word, 0, len(current_word) - 1)
            # print("stemmed:", stemmed_word)
            processed_document += stemmed_word
            current_word = ''
            processed_document += " "
        self.set_abstractVal(processed_document)

    def stem_abstract(self):
        stemmer = PorterStemmer()
        processed_document = ''
        current_word = ''
        document_title = self.get_abstractVal()
        for char in document_title:
            if char.isalpha():
                current_word += char.lower()
            else:
                if current_word:
                    # Apply stemming to the current word
                    stemmed_word = stemmer.stem(current_word, 0, len(current_word) - 1)
                    processed_document += stemmed_word
                    current_word = ''
                processed_document += char.lower()
        self.set_abstractVal(processed_document)
    
    def __str__(self):
        word = self.get_abstractVal()
        if word == "":
            return f"ID: {self.get_id()}\nTitle: {self.get_title()}\nPublisher: {self.get_publisher()}\nAuthor: {self.get_author()}\n"
        else:
            return f"ID: {self.get_id()}\nTitle: {self.get_title()}\nAbstract: {self.get_abstractVal()}\nPublisher: {self.get_publisher()}\nAuthor: {self.get_author()}\n"
