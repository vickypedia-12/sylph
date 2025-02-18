from typing import List, Dict, Set
from .scoring import TFIDFScorer, DocumentScore
from collections import defaultdict

class SearchRanker:
    def __init__(self, total_docs: int):
        self.scorer = TFIDFScorer(total_docs)
        
    def rank_documents(self, 
                      query_terms: List[str],
                      matching_docs: Dict[str, Dict[str, List[int]]],
                      document_metadata: Dict[str, Dict]) -> List[DocumentScore]:
        """Rank documents based on query relevance"""
        
        # Update document frequencies
        for term in query_terms:
            self.scorer.document_frequency[term] = len(matching_docs.get(term, {}))
        
        # Score each document
        scores: List[DocumentScore] = []
        for doc_id in self._get_unique_docs(matching_docs):
            term_positions = self._get_term_positions(doc_id, query_terms, matching_docs)
            
            # Check title and description matches
            metadata = document_metadata.get(doc_id, {})
            title_match = any(term.lower() in metadata.get('title', '').lower() 
                            for term in query_terms)
            desc_match = any(term.lower() in metadata.get('meta_description', '').lower() 
                           for term in query_terms)
            
            score = self.scorer.score_document(
                doc_id=doc_id,
                query_terms=query_terms,
                term_positions=term_positions,
                title_match=title_match,
                description_match=desc_match
            )
            scores.append(score)
        
        # Sort by score descending
        return sorted(scores, key=lambda x: x.score, reverse=True)
    
    def _get_unique_docs(self, matching_docs: Dict[str, Dict[str, List[int]]]) -> Set[str]:
        """Get unique document IDs from matching documents"""
        docs = set()
        for term_docs in matching_docs.values():
            docs.update(term_docs.keys())
        return docs
    
    def _get_term_positions(self, 
                          doc_id: str, 
                          terms: List[str],
                          matching_docs: Dict[str, Dict[str, List[int]]]) -> Dict[str, List[int]]:
        """Get term positions for a document"""
        positions = {}
        for term in terms:
            if term in matching_docs and doc_id in matching_docs[term]:
                positions[term] = matching_docs[term][doc_id]
        return positions