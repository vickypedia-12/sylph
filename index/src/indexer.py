from collections import defaultdict
from typing import Dict, List, Set
from .preprocessor import TextPreprocessor
from .trie import Trie, TrieNode
import json
import os
import logging

logger = logging.getLogger(__name__)

class InvertedIndex:
    def __init__(self):
        self.trie = Trie()
        self.preprocessor = TextPreprocessor()
        self.doc_count = 0

    def add_document(self, doc_id: str, text:str, title:str = "") -> None:
        full_text = f"{title} {text}"
        tokens = self.preprocessor.preprocess(text)

        if not tokens:
            print(f"Warning: No tokens extracted from document {doc_id}")
            return
        
        for position, token in enumerate(tokens):
            if token:
                self.trie.insert(token, doc_id, position)

        self.doc_count += 1
        logger.info(f"Indexed document {doc_id}")

    def save_index(self, filepath:str) -> None:
        try:
            index_data = self._serialize_trie(self.trie.root)

            with open(filepath, 'w', encoding="utf-8") as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved index with {len(index_data)} tokens to {filepath}")

        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise 

    def load_index(self, filepath:str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            self.trie = Trie()
            self._deserialize_trie(index_data)

            logger.info(f"Loaded index with {len(self.trie)} tokens from {filepath}")
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise

    def _serialize_trie(self, node, prefix="") -> Dict:
        result = {
            "is_end": node.is_end,
            "documents": dict(node.documents),
            "children": {}
        }

        for char, child in node.children.items():
            result["children"][char] = self._serialize_trie(child, prefix + char)

        return result
    
    def _deserialize_trie(self, data: Dict, node=None) -> None:
        if not node:
            node = self.trie.root

        node.is_end = data["is_end"]
        node.documents = defaultdict(list, data["documents"])

        for char, child_data in data["children"].items():
            node.children[char] = TrieNode()
            self._deserialize_trie(child_data, node.children[char])