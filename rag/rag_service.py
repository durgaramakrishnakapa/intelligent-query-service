import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from retriever import retrieve_top_chunks


def load_gemini_model():
    """Load Gemini model."""

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-flash")

    return model


def build_context(chunks: list) -> str:
    """Build LLM context from retrieved chunks."""

    context_parts = []

    for item in chunks:
        context_parts.append(item["text"])

    return "\n\n".join(context_parts)


def build_prompt(query: str, context: str) -> str:
    """Build final prompt."""

    prompt = f"""
You are a movie recommendation assistant.

Answer ONLY using the provided catalog context.

If no relevant answer exists, say so.

Return ONLY valid raw JSON.
Do NOT wrap response in markdown.
Do NOT use code fences.

Context:
{context}

User Question:
{query}

Format:
{{
    "answer": "your response",
    "sources": ["show_id_1", "show_id_2"]
}}
"""

    return prompt

def ask_gemini(query: str) -> dict:
    """Run complete RAG pipeline."""

    chunks = retrieve_top_chunks(query)

    context = build_context(chunks)

    model = load_gemini_model()

    prompt = build_prompt(query, context)

    response = model.generate_content(prompt)

    try:
        cleaned_response = response.text.strip()

        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

        result = json.loads(cleaned_response)

    except Exception:
        result = {
            "answer": response.text,
            "sources": [item["show_id"] for item in chunks]
        }

    return result


def main():
    """Test Gemini RAG."""

    query = "Suggest comedy movies from India with strong female lead"

    result = ask_gemini(query)

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()