# embed.py
"""Create vector embeddings for syllabus chunks and questions.

Install the dependency with:
    pip install sentence-transformers
"""

from functools import lru_cache

import numpy as np


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_chunk(chunk: str) -> np.ndarray:
    """Convert one text chunk into a normalized vector."""
    if not isinstance(chunk, str) or not chunk.strip():
        raise ValueError("chunk must be a non-empty string")

    vector = _get_model().encode(
        chunk,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(vector, dtype=np.float32)


def embed_question(question: str) -> np.ndarray:
    """Convert one question into a normalized vector."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")

    vector = _get_model().encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(vector, dtype=np.float32)