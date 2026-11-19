# retrieve.py
"""Return the syllabus chunks most relevant to a question."""

import numpy as np
 

def retrieve(
    chunk_vectors: np.ndarray,
    question_vector: np.ndarray,
    chunks: list[str],
    k: int = 1,
) -> list[str]:
    """Return up to k chunks with the highest cosine similarity.

    Each chunk_vectors[i] must be the embedding for chunks[i].
    """
    chunk_vectors = np.asarray(chunk_vectors, dtype=np.float32)
    question_vector = np.asarray(question_vector, dtype=np.float32)

    if chunk_vectors.ndim != 2:
        raise ValueError("chunk_vectors must be a 2D array")
    if question_vector.ndim != 1:
        raise ValueError("question_vector must be a 1D vector")
    if len(chunk_vectors) != len(chunks):
        raise ValueError("chunk_vectors and chunks must have the same length")
    if chunk_vectors.shape[1] != question_vector.shape[0]:
        raise ValueError("Chunk and question vectors must have the same dimensions")
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer")
    if not chunks:
        return []

    # The vectors are normalized, so dot product gives cosine similarity.
    scores = chunk_vectors @ question_vector
    nearest_indices = np.argsort(-scores, kind="stable")[:k]

    return [chunks[int(index)] for index in nearest_indices]