
import os
from typing import List, Tuple
from dataclasses import dataclass

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import GROQ_API_KEY
from langdetect import detect
from deep_translator import GoogleTranslator
from PyPDF2 import PdfReader

# sentence-transformers
from sentence_transformers import SentenceTransformer

# Groq client

from groq import Groq


# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)

# Embedding model (local)
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # small but effective
embedder = SentenceTransformer(EMBED_MODEL_NAME)

# Generation model to use on Groq
GROQ_CHAT_MODEL = "llama-3.3-70b-versatile"  # example; change if you prefer other Groq models

def chunk_text(text: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks (char-based)."""
    start = 0
    length = len(text)
    chunks = []
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks

def get_embeddings(texts: List[str]) -> np.ndarray:
    """Get embeddings using sentence-transformers (local)."""
    embs = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return np.array(embs, dtype=np.float32)

def top_k_chunks(question: str, chunks: List[str], chunk_embeddings: np.ndarray, k: int = 4):
    """Return top-k chunks most similar to the question."""
    q_emb = embedder.encode([question], convert_to_numpy=True)
    sims = cosine_similarity(q_emb.reshape(1, -1), chunk_embeddings)[0]
    top_idx = np.argsort(sims)[::-1][:k]
    return [(int(i), chunks[i], float(sims[i])) for i in top_idx]

@dataclass
class PDFDocument:
    filename: str
    full_text: str
    chunks: List[str]
    chunk_embeddings: np.ndarray

class MultilingualBackend:
    def __init__(self):
        # self.translator = GoogleTranslator()
        # groq_client is at module level
        self.client = groq_client

    def extract_text_from_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        parts = []
        for p in range(len(reader.pages)):
            try:
                text = reader.pages[p].extract_text() or ""
                parts.append(text)
            except Exception:
                # skip problematic page
                continue
        return "\n".join(parts).strip()

    def load_pdf_document(self, file_path: str) -> PDFDocument:
        full_text = self.extract_text_from_pdf(file_path)
        if not full_text:
            raise ValueError("No text extracted from PDF.")
        chunks = chunk_text(full_text)
        chunk_embeddings = get_embeddings(chunks)
        return PDFDocument(
            filename=os.path.basename(file_path),
            full_text=full_text,
            chunks=chunks,
            chunk_embeddings=chunk_embeddings
        )

    def detect_language(self, text: str) -> str:
        try:
            code = detect(text)
            # googletrans maps codes to names
            langname = GoogleTranslator().LANGUAGES.get(code, code)
            return langname.title() if isinstance(langname, str) else code
        except Exception:
            return "unknown"

    def translate_to_english(self, text):
        try:
            return GoogleTranslator(source='auto', target='en').translate(text)
        except:
            return text


    def translate_from_english(self, text, dest_code):
        try:
            return GoogleTranslator(source='en', target=dest_code).translate(text)
        except:
            return text


    def infer_lang_code(self, language_name_or_code: str) -> str:
        s = (language_name_or_code or "").strip().lower()
        if not s:
            return "en"
        mapping = {
            "english": "en", "en": "en",
            "hindi": "hi", "hi": "hi",
            "gujarati": "gu", "gu": "gu",
            "marathi": "mr", "mr": "mr",
            "tamil": "ta", "ta": "ta",
            "bengali": "bn", "bn": "bn", "bangla": "bn",
            "kannada": "kn", "kn": "kn",
            "telugu": "te", "te": "te",
        }
        return mapping.get(s, s[:2])

    def _call_groq_chat(self, system_prompt: str, user_prompt: str, model: str = GROQ_CHAT_MODEL, max_tokens: int = 512) -> str:
        """
        Call Groq chat completions. Returns the assistant text.
        Response structures can differ; attempt to read both attr and dict styles.
        """
        try:
            resp = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.0,
            )
            # try dict-like access
            if isinstance(resp, dict):
                # common shapes: resp['choices'][0]['message']['content']
                choices = resp.get("choices") or []
                if choices:
                    first = choices[0]
                    # nested message
                    message = first.get("message") or first.get("text") or {}
                    if isinstance(message, dict):
                        return message.get("content") or message.get("text") or str(first)
                    # if message is string
                    if isinstance(message, str):
                        return message
                # fallback: stringified resp
                return str(resp)
            else:
                # object-like: try attribute access
                try:
                    return resp.choices[0].message.content
                except Exception:
                    # final fallback
                    return str(resp)
        except Exception as e:
            # bubble up a readable error
            raise RuntimeError(f"Groq chat request failed: {e}")

    def answer_question(self, pdf_doc: PDFDocument, user_question: str, user_lang_code: str = "en") -> dict:
        detected_language = self.detect_language(user_question)
        question_en = self.translate_to_english(user_question)
        top = top_k_chunks(question_en, pdf_doc.chunks, pdf_doc.chunk_embeddings, k=4)
        context_text = "\n\n---\n\n".join([f"(Score: {score:.4f})\n{chunk}" for (_i, chunk, score) in top])

        system_prompt = (
            "You are an assistant. Answer using ONLY the provided context from a PDF. "
            "If the answer is not present, say you cannot find it in the document. Do NOT hallucinate."
        )
        user_prompt = (
            f"Context (from PDF):\n\n{context_text}\n\n"
            f"Question (in English): {question_en}\n\n"
            "Answer concisely and cite short context excerpts if helpful."
        )

        answer_en = self._call_groq_chat(system_prompt, user_prompt)

        dest_code = self.infer_lang_code(user_lang_code)
        answer_translated = self.translate_from_english(answer_en, dest_code)

        return {
            "detected_language": detected_language,
            "question_english": question_en,
            "answer_english": answer_en,
            "answer_translated": answer_translated,
            "used_chunks": [{"snippet": chunk, "score": score} for (_i, chunk, score) in top]
        }
