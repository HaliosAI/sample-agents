from __future__ import annotations

"""
search_engine.py
Zero-dependency in-memory product search engine over products.csv.
Uses BM25-style term weighting with title and category field boosts.
"""

import csv
import math
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional

DEFAULT_CSV_PATH = Path(__file__).resolve().parent / "products.csv"

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into alphanumeric words."""
    if not text:
        return []
    return re.findall(r'\b[a-z0-9]+\b', text.lower())

class CsvProductCatalog:
    """In-memory product catalog with fast lexical and relevance search."""
    
    def __init__(self, csv_path: Optional[Path] = None):
        self.csv_path = Path(csv_path) if csv_path else DEFAULT_CSV_PATH
        self.products: List[Dict[str, Any]] = []
        self.doc_freqs: Counter = Counter()
        self.total_docs: int = 0
        self.avg_doc_len: float = 0.0
        self.doc_token_counts: List[Counter] = []
        self.doc_lengths: List[int] = []
        self.load_catalog()

    def load_catalog(self) -> None:
        """Load and index products from CSV."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Product catalog CSV not found: {self.csv_path}")

        self.products.clear()
        self.doc_freqs.clear()
        self.doc_token_counts.clear()
        self.doc_lengths.clear()

        total_length = 0
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.products.append(row)
                
                # Combine fields for search document with field weighting
                name_tokens = tokenize(row.get("product_name", ""))
                cat_tokens = tokenize(row.get("category", ""))
                mat_tokens = tokenize(row.get("material", "") + " " + row.get("wood_finish", ""))
                desc_tokens = tokenize(row.get("description", ""))

                # Synthetic document with repetitions representing field importance
                # Name (3x weight), Category (2x weight), Material/Finish (2x), Desc (1x)
                doc_tokens = (name_tokens * 3) + (cat_tokens * 2) + (mat_tokens * 2) + desc_tokens
                doc_len = len(doc_tokens)
                total_length += doc_len
                
                counts = Counter(doc_tokens)
                self.doc_token_counts.append(counts)
                self.doc_lengths.append(doc_len)
                
                # Unique terms in doc for IDF
                for term in counts:
                    self.doc_freqs[term] += 1

        self.total_docs = len(self.products)
        self.avg_doc_len = (total_length / self.total_docs) if self.total_docs > 0 else 1.0

    def score_bm25(self, query_tokens: List[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        """Compute BM25 relevance score for a document."""
        score = 0.0
        doc_counts = self.doc_token_counts[doc_idx]
        doc_len = self.doc_lengths[doc_idx]
        
        for q in query_tokens:
            if q not in doc_counts:
                continue
            
            tf = doc_counts[q]
            df = self.doc_freqs.get(q, 0)
            idf = math.log(1.0 + (self.total_docs - df + 0.5) / (df + 0.5))
            
            tf_component = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len)))
            score += idf * tf_component
            
        return score

    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search products by query string and return top ranked products."""
        if not query or not query.strip():
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_lower = query.lower().strip()
        scored_products = []

        for idx, prod in enumerate(self.products):
            base_score = self.score_bm25(query_tokens, idx)
            if base_score <= 0:
                continue

            name_lower = prod.get("product_name", "").lower()
            name_tokens_set = set(tokenize(name_lower))
            matching_title_tokens = sum(1 for q in query_tokens if q in name_tokens_set)
            
            # Boost for tokens matching the product title directly
            if query_tokens:
                title_ratio = matching_title_tokens / len(query_tokens)
                base_score += title_ratio * 15.0

            # Strong boost if all query tokens appear in product title
            if query_tokens and all(q in name_tokens_set for q in query_tokens):
                base_score += 25.0

            # Additional boost for exact title substring match
            if query_lower in name_lower:
                base_score += 15.0
            
            scored_products.append((base_score, prod))

        # Sort descending by score
        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_products[:n_results]]

    def search_formatted(self, query: str, n_results: int = 3) -> str:
        """Search and format results suitable for LLM tool consumption."""
        results = self.search(query, n_results=n_results)
        if not results:
            return "No products found matching the query."

        output = []
        for prod in results:
            name = prod.get("product_name", "")
            desc = prod.get("description", "")
            category = prod.get("category", "")
            material = prod.get("material", "")
            wood_finish = prod.get("wood_finish", "")
            link = prod.get("product_link", "")

            details_parts = [desc]
            if material:
                details_parts.append(f"Material: {material}")
            if wood_finish:
                details_parts.append(f"Finish: {wood_finish}")
            if category:
                details_parts.append(f"Category: {category}")

            details = " | ".join(details_parts)
            output.append(f"Name: {name}\nDetails: {details}\nLink: {link}")

        return "\n\n".join(output)

# Singleton global catalog instance
_global_catalog: Optional[CsvProductCatalog] = None

def get_product_catalog() -> CsvProductCatalog:
    global _global_catalog
    if _global_catalog is None:
        _global_catalog = CsvProductCatalog()
    return _global_catalog

def search_products(query: str, n_results: int = 3) -> str:
    """Convenience functional interface for search."""
    return get_product_catalog().search_formatted(query, n_results=n_results)
