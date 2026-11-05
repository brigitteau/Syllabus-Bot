"""Rank syllabus chunks by their similarity to a question embedding.

Chunk embeddings are created once when a PDF is uploaded and reused for
later questions. The project's embed_question function is passed in.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any


Vector = Sequence[float]
EmbeddingFunction = Callable[[str], Vector]


def _get_value(item: Any, key: str, default: Any = None) -> Any:
    """Read a field from either a dictionary-like chunk or an object."""
    if isinstance(item, Mapping):
        return item.get(key, default)
    return getattr(item, key, default)


def _cosine_similarity(left: Vector, right: Vector) -> float:
    """Return cosine similarity, validating dimensions and zero vectors."""
    if len(left) != len(right):
        raise ValueError(
            f"Embedding dimensions do not match ({len(left)} and {len(right)})."
        )

    dot = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) ** 2 for value in left))
    right_norm = math.sqrt(sum(float(value) ** 2 for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def retrieve(
    question: str,
    chunks: Iterable[Any],
    *,
    embed_question: EmbeddingFunction,
    top_k: int = 3,
    chunk_embeddings: Sequence[Vector] | None = None,
) -> list[dict[str, Any]]:
    """Return the top_k chunks most relevant to the question.

    Args:
        question: The user's question about the syllabus.
        chunks: Strings or dictionaries/objects with a "text" field.
            Chunks may also contain an "embedding" field and optional
            "source" metadata.
        embed_question: The project's question-embedding function.
        top_k: Maximum number of results to return.
        chunk_embeddings: Optional precomputed chunk vectors in the same
            order as chunks. If omitted, each chunk must contain an
            "embedding" field.

    Returns:
        A list of dictionaries, highest similarity first. Each has
        "text", "score", "source", and "index" keys.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    chunk_list = list(chunks)
    if not chunk_list:
        return []

    question_vector = embed_question(question.strip())
    if len(question_vector) == 0:
        raise ValueError("embed_question returned an empty vector")

    if chunk_embeddings is not None and len(chunk_embeddings) != len(chunk_list):
        raise ValueError(
            "chunk_embeddings must contain one vector for every chunk "
            f"({len(chunk_embeddings)} vectors for {len(chunk_list)} chunks)."
        )

    ranked = []

    for index, chunk in enumerate(chunk_list):
        if chunk_embeddings is not None:
            vector = chunk_embeddings[index]
        else:
            vector = _get_value(chunk, "embedding")

        if vector is None:
            raise ValueError(
                f"Chunk {index} has no embedding. Pass chunk_embeddings or "
                "include an 'embedding' field on each chunk."
            )

        if isinstance(chunk, str):
            text = chunk
        else:
            text = _get_value(chunk, "text", "")

        if not isinstance(text, str):
            raise TypeError(f"Chunk {index} text must be a string")

        ranked.append(
            {
                "text": text,
                "score": _cosine_similarity(question_vector, vector),
                "source": _get_value(chunk, "source"),
                "index": index,
            }
        )

    ranked.sort(key=lambda result: result["score"], reverse=True)
    return ranked[:top_k]"""Rank syllabus chunks by their similarity to a question embedding.

Chunk embeddings are created once when a PDF is uploaded and reused for
later questions. The project's embed_question function is passed in.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any


Vector = Sequence[float]
EmbeddingFunction = Callable[[str], Vector]


def _get_value(item: Any, key: str, default: Any = None) -> Any:
    """Read a field from either a dictionary-like chunk or an object."""
    if isinstance(item, Mapping):
        return item.get(key, default)
    return getattr(item, key, default)


def _cosine_similarity(left: Vector, right: Vector) -> float:
    """Return cosine similarity, validating dimensions and zero vectors."""
    if len(left) != len(right):
        raise ValueError(
            f"Embedding dimensions do not match ({len(left)} and {len(right)})."
        )

    dot = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) ** 2 for value in left))
    right_norm = math.sqrt(sum(float(value) ** 2 for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def retrieve(
    question: str,
    chunks: Iterable[Any],
    *,
    embed_question: EmbeddingFunction,
    top_k: int = 3,
    chunk_embeddings: Sequence[Vector] | None = None,
) -> list[dict[str, Any]]:
    """Return the top_k chunks most relevant to the question.

    Args:
        question: The user's question about the syllabus.
        chunks: Strings or dictionaries/objects with a "text" field.
            Chunks may also contain an "embedding" field and optional
            "source" metadata.
        embed_question: The project's question-embedding function.
        top_k: Maximum number of results to return.
        chunk_embeddings: Optional precomputed chunk vectors in the same
            order as chunks. If omitted, each chunk must contain an
            "embedding" field.

    Returns:
        A list of dictionaries, highest similarity first. Each has
        "text", "score", "source", and "index" keys.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    chunk_list = list(chunks)
    if not chunk_list:
        return []

    question_vector = embed_question(question.strip())
    if len(question_vector) == 0:
        raise ValueError("embed_question returned an empty vector")

    if chunk_embeddings is not None and len(chunk_embeddings) != len(chunk_list):
        raise ValueError(
            "chunk_embeddings must contain one vector for every chunk "
            f"({len(chunk_embeddings)} vectors for {len(chunk_list)} chunks)."
        )

    ranked = []

    for index, chunk in enumerate(chunk_list):
        if chunk_embeddings is not None:
            vector = chunk_embeddings[index]
        else:
            vector = _get_value(chunk, "embedding")

        if vector is None:
            raise ValueError(
                f"Chunk {index} has no embedding. Pass chunk_embeddings or "
                "include an 'embedding' field on each chunk."
            )

        if isinstance(chunk, str):
            text = chunk
        else:
            text = _get_value(chunk, "text", "")

        if not isinstance(text, str):
            raise TypeError(f"Chunk {index} text must be a string")

        ranked.append(
            {
                "text": text,
                "score": _cosine_similarity(question_vector, vector),
                "source": _get_value(chunk, "source"),
                "index": index,
            }
        )

    ranked.sort(key=lambda result: result["score"], reverse=True)
    return ranked[:top_k]