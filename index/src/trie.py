from typing import Dict, List, Set, Optional
from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end = False
        self.documents: Dict[str, List[int]] = defaultdict(list)

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._size = 0

    def insert(self, word: str, doc_id: str, position: int) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end = True
        node.documents[doc_id].append(position)
        self._size += 1

    def search(self, word: str) -> Dict[str, List[int]]:
        node = self._find_node(word)
        return node.documents if node and node.is_end else {}

    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]

        return node

    def starts_with(self, prefix:str) -> Set[str]:
        node = self._find_node(prefix)
        if not node:
            return set()

        documents = set()
        self._collect_documents(node, documents)
        return documents

    def _collect_documents(self, node: TrieNode, documents: Set[str]) -> None:
        if node.is_end:
            documents.update(node.documents.keys())

        for child in node.children.values():
            self._collect_documents(child, documents)

        
    def __len__(self) -> int:
        return self._size