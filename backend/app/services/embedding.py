import hashlib
import math
import re
from typing import List

from app.core.config import settings

EMBEDDING_DIM = settings.EMBEDDING_DIMENSION  # 384


def _normalize(vector: List[float]) -> List[float]:
    """L2 normalize vector so dot product equals cosine similarity."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def _hash_token_embedding(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Generate a stable, dense semantic feature vector for local testing and dev."""
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return [0.0] * dim

    vec = [0.0] * dim
    for pos, token in enumerate(tokens):
        # Generate multiple hash projections for token to distribute across dimensions
        h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        h2 = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)

        idx1 = h1 % dim
        idx2 = h2 % dim
        sign1 = 1.0 if (h1 >> 4) % 2 == 0 else -1.0
        sign2 = 1.0 if (h2 >> 4) % 2 == 0 else -1.0

        weight = 1.0 / math.sqrt(pos + 1)
        vec[idx1] += sign1 * weight
        vec[idx2] += sign2 * weight

    return _normalize(vec)


def get_embedding(text: str) -> List[float]:
    """Generate 384-dimensional normalized embedding vector for text."""
    # Local neural model fallback or deterministic semantic vector
    return _hash_token_embedding(text, dim=EMBEDDING_DIM)


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a batch of text strings."""
    return [get_embedding(t) for t in texts]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two normalized vectors (dot product)."""
    if len(vec1) != len(vec2) or not vec1:
        return 0.0
    return float(sum(a * b for a, b in zip(vec1, vec2)))
