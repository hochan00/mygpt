from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from api.core.config import settings


embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)


def get_llm(temperature: float | None = None) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=temperature or settings.GEMINI_TEMPERATURE,
    )


tokenizer = AutoTokenizer.from_pretrained(settings.POLYGLOT_MODEL)
polyglot_model = AutoModelForCausalLM.from_pretrained(
    settings.POLYGLOT_MODEL, dtype=torch.float32
)
polyglot_model.eval()
