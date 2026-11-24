import logging
from typing import List, Dict, Any, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are DocuMind AI, an evidence-grounded document question-answering assistant.
Answer the user's question STRICTLY based on the provided document excerpts below.
Rules:
1. Only state facts directly supported by the provided excerpts.
2. If the excerpts do not contain enough information to answer the question, say: 'Based on the uploaded documents, there is insufficient evidence to answer this question.'
3. Do not assume or extrapolate information beyond what is stated.
4. Keep the answer concise, accurate, and professional.
"""


def format_context_prompt(question: str, chunks: List[Dict[str, Any]]) -> str:
    """Format prompt with retrieved excerpts and instructions."""
    context_blocks = []
    for idx, c in enumerate(chunks, start=1):
        page_info = f" (Page {c['page_number']})" if c.get("page_number") else ""
        context_blocks.append(f"[Excerpt {idx} - {c['document_name']}{page_info}]:\n{c['content']}")

    context_str = "\n\n".join(context_blocks)
    return f"{SYSTEM_PROMPT}\n\nDocument Excerpts:\n{context_str}\n\nQuestion: {question}\n\nAnswer:"


def generate_llm_response(question: str, chunks: List[Dict[str, Any]]) -> Tuple[str, bool]:
    """Generate answer from Google Gemini API or grounded local synthesizer."""
    if not chunks:
        return "Based on the uploaded documents, there is insufficient evidence to answer this question.", False

    # Check if Gemini API Key is configured
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key":
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = format_context_prompt(question, chunks)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL or "gemini-1.5-flash",
                contents=prompt,
            )
            answer_text = response.text.strip() if response.text else ""
            if answer_text:
                return answer_text, True
        except Exception as e:
            logger.warning("Gemini API call failed (%s). Falling back to grounded synthesis.", e)

    # Fallback synthesizer: returns facts directly from top matching excerpts
    relevant_texts = [c["content"] for c in chunks[:3]]
    synthesized = " ".join(relevant_texts)
    return synthesized, True
