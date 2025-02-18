from dataclasses import dataclass
from typing import Dict, List
import math

@dataclass
class DocumentScore:
    doc_id: str
    score: float
    title_match: bool
    description_match: bool
    positions: List[int]

class TFIDFScorer:
    def __init__(self, total_docs: int):
        self.total_docs = total_docs
        self.document_frequency: Dict[str, int] = {}
    
    def compute_tf(self, term: str, positions: List[int]) -> float:
        return 1 + math.log10(len(positions)) if positions else 0
    
    def compute_idf(self, term: str, doc_count: int) -> float:
        return math.log10(self.total_docs / (doc_count + 1))
    
    def score_document(self, 
                      doc_id: str, 
                      query_terms: List[str],
                      term_positions: Dict[str, List[int]], 
                      title_match: bool = False,
                      description_match: bool = False) -> DocumentScore:

        score = 0.0
        all_positions = []
        
        for term in query_terms:
            if term in term_positions:
                term_pos = term_positions[term]
                all_positions.extend(term_pos)
                tf = self.compute_tf(term, term_pos)
                idf = self.compute_idf(term, self.document_frequency.get(term, 0))
                score = tf * idf

                position_boost = 1.0 / (1 + min(term_pos)) if term_pos else 1.0
                score += score * position_boost
        
        # Boost scores based on matches
        if title_match:
            score *= 1.5
        if description_match:
            score *= 1.2
            
        return DocumentScore(
            doc_id=doc_id,
            score=score,
            title_match=title_match,
            description_match=description_match,
            positions=sorted(all_positions)
        )