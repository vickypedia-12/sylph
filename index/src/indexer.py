from collections import defaultdict
from typing import Dict, List, Set
from .preprocessor import TextPreprocessor
import json
import os
import logging
logger = logging.getLogger(__name__)

class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, List[int]] = defaultdict(lambda: defaultdict(list))
        self.preprocessor = TextPreprocessor()

    def add_document(self, doc_id: str, text:str, title:str = "") -> None:
        full_text = f"{title} {text}"
        tokens = self.preprocessor.preprocess(text)
        if not tokens:
            print(f"Warning: No tokens extracted from document {doc_id}")
            return
        for position, token in enumerate(tokens):
            if token:
                self.index[token][doc_id].append(position)
        logger.info(f"Indexed document {doc_id}")

    def save_index(self, filepath:str) -> None:
        try:
            index_dict = {}
            for token, postings in self.index.items():
                if postings:
                    index_dict[token] = dict(postings)

            with open(filepath, 'w', encoding="utf-8") as f:
                json.dump(index_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved index with {len(index_dict)} tokens to {filepath}")

        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise 

    def load_index(self, filepath:str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_index = json.load(f)

            self.index = defaultdict(lambda: defaultdict(list))
            for token, postings in loaded_index.items():
                for doc_id, postings in postings.items():
                    self.index[token] = defaultdict(list, postings)

            logger.info(f"Loaded index with {len(self.index)} tokens from {filepath}")
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise
