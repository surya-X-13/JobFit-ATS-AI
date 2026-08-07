"""
core/embeddings.py
Semantic embedding and cosine similarity using SentenceTransformers.
Model: all-mpnet-base-v2 (best general-purpose semantic similarity)
"""
from __future__ import annotations
import numpy as np
from functools import lru_cache
from typing import Optional


MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
_model_cache: Optional[object] = None


def get_model():
    """Load and cache the SentenceTransformer model (singleton)."""
    global _model_cache
    if _model_cache is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model_cache = SentenceTransformer(MODEL_NAME)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
    return _model_cache


def embed(text: str) -> np.ndarray:
    """
    Embed a single text string into a dense vector.
    
    Args:
        text: Input text (max ~512 tokens; longer text is auto-truncated)
    Returns:
        1D numpy array (768 dims for mpnet)
    """
    model = get_model()
    # Truncate to ~4000 chars to stay within token limits
    truncated = text[:4000] if len(text) > 4000 else text
    vec = model.encode(truncated, convert_to_numpy=True, normalize_embeddings=True)
    return vec


def embed_batch(texts: list[str]) -> np.ndarray:
    """Embed multiple texts at once (more efficient than one-by-one)."""
    model = get_model()
    truncated = [t[:4000] for t in texts]
    vecs = model.encode(truncated, convert_to_numpy=True, normalize_embeddings=True)
    return vecs


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two normalized vectors.
    Since we normalize embeddings, dot product == cosine similarity.
    
    Returns:
        Float in [0, 1]
    """
    # Both vectors are L2-normalized by SentenceTransformer
    sim = float(np.dot(vec1, vec2))
    # Clamp to [0, 1] to handle floating point edge cases
    return max(0.0, min(1.0, sim))


def semantic_similarity_score(text1: str, text2: str) -> float:
    """
    Compute semantic similarity between two texts.
    
    Returns:
        Float in [0, 1]
    """
    v1 = embed(text1)
    v2 = embed(text2)
    return cosine_similarity(v1, v2)


def section_similarities(resume_sections: dict[str, str], jd_text: str) -> dict[str, float]:
    """
    Compute semantic similarity between each resume section and the JD.
    
    Returns:
        Dict mapping section name → similarity score [0, 1]
    """
    jd_vec = embed(jd_text)
    results = {}
    for section, content in resume_sections.items():
        if section == "full_text" or not content.strip():
            continue
        sec_vec = embed(content)
        results[section] = round(cosine_similarity(sec_vec, jd_vec), 4)
    return results
