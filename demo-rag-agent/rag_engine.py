"""Hybrid RAG Search Engine (Semantic Vector + BM25 Keyword Search).

Universal & OpenRouter compatible: works with OpenAI, OpenRouter, Together,
Ollama, Voyage, or local TF-IDF fallback.
"""

import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class RAGEngine:
    def __init__(
        self,
        corpus_dir: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        if corpus_dir is None:
            corpus_dir = str(Path(__file__).parent / "corpus")
        self.corpus_dir = corpus_dir

        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.embedding_model = (
            embedding_model
            or os.getenv("OPENAI_EMBEDDING_MODEL")
            or "text-embedding-3-small"
        )

        self.chunks: List[Dict[str, Any]] = []
        self.doc_store: Dict[str, str] = {}
        self.embeddings: Optional[np.ndarray] = None
        self._client = None

        if self.api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except Exception:
                self._client = None

        self.load_corpus()

    def load_corpus(self) -> None:
        """Read all markdown files from the corpus directory and index them."""
        self.chunks = []
        self.doc_store = {}
        corpus_path = Path(self.corpus_dir)
        if not corpus_path.exists():
            return

        for filepath in corpus_path.glob("*.md"):
            doc_id = filepath.stem
            content = filepath.read_text(encoding="utf-8")
            self.add_document(doc_id=doc_id, content=content, filename=filepath.name)

        self._build_index()

    def add_document(self, doc_id: str, content: str, filename: Optional[str] = None) -> None:
        """Add and chunk a document into the search engine."""
        self.doc_store[doc_id] = content
        filename = filename or f"{doc_id}.md"

        sections = re.split(r"\n(?=##?\s)", content)
        doc_title = sections[0].split("\n")[0].replace("#", "").strip() if sections else doc_id

        for idx, section in enumerate(sections):
            clean_section = section.strip()
            if not clean_section:
                continue

            lines = clean_section.split("\n")
            section_title = lines[0].replace("#", "").strip() if lines else f"Section {idx+1}"

            self.chunks.append(
                {
                    "chunk_id": f"{doc_id}_{idx}",
                    "doc_id": doc_id,
                    "filename": filename,
                    "doc_title": doc_title,
                    "section_title": section_title,
                    "content": clean_section,
                }
            )

    def _build_index(self) -> None:
        """Build embedding matrix for semantic vector search."""
        if not self.chunks:
            return

        texts = [f"{c['doc_title']} - {c['section_title']}\n{c['content']}" for c in self.chunks]

        if self._client:
            try:
                response = self._client.embeddings.create(
                    input=texts,
                    model=self.embedding_model,
                )
                self.embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
                return
            except Exception as e:
                # If provider does not support embeddings, fall back gracefully to local BM25/TFIDF
                pass

        self._build_local_tfidf(texts)

    def _build_local_tfidf(self, texts: List[str]) -> None:
        """Fallback in-memory TF-IDF vectorizer (Works with 0 API keys)."""
        vocab: Dict[str, int] = {}
        for text in texts:
            for word in re.findall(r"\w+", text.lower()):
                if word not in vocab:
                    vocab[word] = len(vocab)

        self._vocab = vocab
        matrix = np.zeros((len(texts), len(vocab)), dtype=np.float32)
        for i, text in enumerate(texts):
            counts = Counter(re.findall(r"\w+", text.lower()))
            for word, count in counts.items():
                if word in vocab:
                    matrix[i, vocab[word]] = count

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings = matrix / norms

    def _bm25_search(self, query: str, top_k: int = 10) -> List[tuple[int, float]]:
        """Keyword BM25 score calculation across chunks."""
        query_terms = re.findall(r"\w+", query.lower())
        if not query_terms or not self.chunks:
            return []

        doc_freqs = Counter()
        chunk_counters = []
        for c in self.chunks:
            words = re.findall(r"\w+", c["content"].lower())
            counts = Counter(words)
            chunk_counters.append(counts)
            for term in set(query_terms):
                if term in counts:
                    doc_freqs[term] += 1

        scores = []
        n_docs = len(self.chunks)
        avg_len = sum(sum(cc.values()) for cc in chunk_counters) / max(1, n_docs)
        k1, b = 1.5, 0.75

        for i, counts in enumerate(chunk_counters):
            doc_len = sum(counts.values())
            score = 0.0
            for term in query_terms:
                if term in counts:
                    idf = math.log(1 + (n_docs - doc_freqs[term] + 0.5) / (doc_freqs[term] + 0.5))
                    tf = counts[term]
                    denom = tf + k1 * (1 - b + b * (doc_len / max(1, avg_len)))
                    score += idf * (tf * (k1 + 1)) / max(1e-5, denom)
            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _vector_search(self, query: str, top_k: int = 10) -> List[tuple[int, float]]:
        """Vector similarity search supporting any arbitrary embedding dimensions."""
        if self.embeddings is None or not self.chunks:
            return []

        query_vec = None
        if self._client:
            try:
                res = self._client.embeddings.create(
                    input=[query],
                    model=self.embedding_model,
                )
                query_vec = np.array(res.data[0].embedding, dtype=np.float32)
            except Exception:
                query_vec = None

        if query_vec is None:
            query_vec = np.zeros(len(getattr(self, "_vocab", {})), dtype=np.float32)
            for word in re.findall(r"\w+", query.lower()):
                if hasattr(self, "_vocab") and word in self._vocab:
                    query_vec[self._vocab[word]] += 1
            norm = np.linalg.norm(query_vec)
            if norm > 0:
                query_vec /= norm

        sims = np.dot(self.embeddings, query_vec)
        top_indices = np.argsort(sims)[::-1][:top_k]
        return [(int(idx), float(sims[idx])) for idx in top_indices]

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Hybrid Search combining Vector + BM25 via Reciprocal Rank Fusion (RRF)."""
        if not self.chunks:
            return []

        bm25_ranks = {idx: rank for rank, (idx, _) in enumerate(self._bm25_search(query, top_k=10))}
        vector_ranks = {idx: rank for rank, (idx, _) in enumerate(self._vector_search(query, top_k=10))}

        rrf_scores: Dict[int, float] = {}
        k = 60.0
        all_indices = set(bm25_ranks.keys()).union(set(vector_ranks.keys()))

        for idx in all_indices:
            score = 0.0
            if idx in bm25_ranks:
                score += 1.0 / (k + bm25_ranks[idx])
            if idx in vector_ranks:
                score += 1.0 / (k + vector_ranks[idx])
            rrf_scores[idx] = score

        ranked_indices = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for idx, score in ranked_indices:
            chunk = dict(self.chunks[idx])
            chunk["score"] = float(score)
            results.append(chunk)

        return results

    def get_document(self, doc_id: str) -> Optional[str]:
        """Retrieve full original document by document ID."""
        return self.doc_store.get(doc_id)
