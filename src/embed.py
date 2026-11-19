import numpy as np
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

client = genai.Client()

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
BATCH_SIZE = 100


def _normalize(values):
    vector = np.array(values)
    return vector / np.linalg.norm(vector)


def _chunk_to_text(chunk):
    if isinstance(chunk, str):
        return chunk
    section = chunk.get("section")
    text = chunk["text"]
    return f"{section}: {text}" if section else text


def embed_question(question):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBED_DIM,
        ),
    )
    return _normalize(result.embeddings[0].values)


def embed_chunks(chunks):
    texts = [_chunk_to_text(c) for c in chunks]
    vectors = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBED_DIM,
            ),
        )
        vectors.extend(_normalize(e.values) for e in result.embeddings)
    return vectors


def embed_chunk(chunk):
    return embed_chunks([chunk])[0]
