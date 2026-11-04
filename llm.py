import time

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

client = genai.Client()

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]

INSTRUCTIONS = (
    "You are a course syllabus assistant. Answer the student's question "
    "using ONLY the syllabus excerpts provided. If the answer is not in the "
    "excerpts, say you couldn't find it in the syllabus. Be concise."
)


def generate_answer(question, chunks):
    # Accept a single chunk (string) or a list of chunks
    if isinstance(chunks, str):
        chunks = [chunks]

    context = "\n\n---\n\n".join(chunks)
    prompt = f"Syllabus excerpts:\n{context}\n\nQuestion: {question}"

    last_error = None
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCTIONS,
                        temperature=0.2,
                    ),
                )
                return response.text
            except Exception as e:
                last_error = e
                err = str(e)
                if "503" in err or "429" in err:
                    time.sleep(2 ** attempt)
                elif "404" in err:
                    break
                else:
                    return f"Sorry, something went wrong calling Gemini: {e}"

    return f"Gemini is unavailable right now. Please try again in a minute. ({last_error})"