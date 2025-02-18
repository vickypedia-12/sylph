from typing import List, Dict, Set
from collections import defaultdict
from .preprocessor import TextPreprocessor
from .indexer import InvertedIndex
from ranking.src.ranker import SearchRanker, TFIDFScorer, DocumentScore

class SearchEngine:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.preprocessor = TextPreprocessor()
        self.scorer =  TFIDFScorer(total_docs=max(1, index.doc_count))
        
    def search(self, query: str, max_results: int = 10) -> List[str]:
        query_tokens = self.preprocessor.preprocess(query)
        if not query_tokens:
            return []
        matching_docs: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))

        for token in query_tokens:
            results = self.index.trie.search(token)
            if results:
                self.scorer.document_frequency[token] = len(results)
                for doc_id, positions in results.items():
                    matching_docs[doc_id][token] = positions

        scored_docs: List[DocumentScore] = []
        for doc_id, term_positions in matching_docs.items():
            doc_meta = next((doc for doc in self.index.get_documents() if doc['url'] == doc_id), {})
            
            # Check for matches in title and description
            title = doc_meta.get('title', '').lower()
            description = doc_meta.get('meta_description', '').lower()
            
            title_match = any(token in title for token in query_tokens)
            desc_match = any(token in description for token in query_tokens)
            
            # Score document
            score = self.scorer.score_document(
                doc_id=doc_id,
                query_terms=query_tokens,
                term_positions=term_positions,
                title_match=title_match,
                description_match=desc_match
            )
            scored_docs.append(score)

        scored_docs.sort(key=lambda x: x.score, reverse=True)
        return [doc.doc_id for doc in scored_docs[:max_results]]
