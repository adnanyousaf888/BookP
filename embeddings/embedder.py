# embeddings/embedder.py

from typing import List
from langchain_openai import OpenAIEmbeddings
from settings import OPENAI_API_KEY

_embedding_model = OpenAIEmbeddings(
  model="text-embedding-3-small",
  api_key=OPENAI_API_KEY,
)

def embed_text(text: str) -> List[float]:
  """Return a single embedding vector for the given text."""
  return _embedding_model.embed_query(text)
