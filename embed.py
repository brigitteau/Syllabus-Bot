import numpy as np
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

client = genai.Client()

EMBED_MODEL = "gemini-embedding-001"   # chunks must use this SAME model later
EMBED_DIM = 768


def embed_question(question):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBED_DIM,
        ),
    )
    vector = np.array(result.embeddings[0].values)
    return vector / np.linalg.norm(vector)   # normalize to length 1
