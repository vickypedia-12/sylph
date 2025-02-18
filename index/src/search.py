from typing import List, Dict, Set
from collections import defaultdict
from .preprocessor import TextPreprocessor
from .indexer import InvertedIndex

class SearchEngine:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.preprocessor = TextPreprocessor()
        
    def search(self, query: str, max_results: int = 10) -> List[str]:
        query_tokens = self.preprocessor.preprocess(query)
        matching_docs: Dict[str, int] = defaultdict(int)

        for token in query_tokens:
            if token in self.index.index:
                for doc_id in self.index.index[token]:
                    matching_docs[doc_id] += 1


        sorted_results = sorted(
            matching_docs.items(),
            key = lambda x: x[1],
            reverse=True
        )

        return [doc_id for doc_id,_ in sorted_results[:max_results]]
