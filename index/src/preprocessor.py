import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from typing import List

class TextPreprocessor:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def preprocess(self,text: str) -> List[str]:
        tokens = word_tokenize(text.lower())
        tokens = [
            token for token in tokens
            if token.isalpha() and token not in self.stop_words
        ]

        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]

        return stemmed_tokens
