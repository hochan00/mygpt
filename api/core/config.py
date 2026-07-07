from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    LANGSMITH_TRACING: bool = True
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "mygpt"

    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.3

    EMBEDDING_MODEL: str = "jhgan/ko-sroberta-multitask"

    RAG_TOP_K: int = 3
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 100
    CHROMA_PERSIST_DIR: str = "data/chroma_db"

    POLYGLOT_MODEL: str = "EleutherAI/polyglot-ko-1.3b"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
