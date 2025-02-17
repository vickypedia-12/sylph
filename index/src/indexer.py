from collections import defaultdict
from typing import Dict, List, Set
from .preprocessor import TextPreprocessor
import json

class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, List[int]] = defaultdict(lambda: defaultdict(list))
        self.preprocessor = TextPreprocessor()

    def add_document(self, doc_id: str, text:str, title:str = "") -> None:
        tokens = self.preprocessor.preprocess(text)
        for position, token in enumerate(tokens):
            self.index[token][doc_id].append(position)

    def save_index(self, filepath:str) -> None:
        index_data = {
            token: dict(postings)
            for token, postings in self.index.items()
        }

        with open(filepath, 'w') as f:
            json.dump(index_data, f)

    def load_index(self, filepath:str) -> None:
        with open(filepath, 'r') as f:
            loaded_index = json.load(f)

        self.index = defaultdict(lambda: defaultdict(list))
        for token, postings in loaded_index.items():
            for doc_id, positions in postings.items():
                self.index[token] = defaultdict(list, postings)
