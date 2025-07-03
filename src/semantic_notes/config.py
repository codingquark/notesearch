"""Configuration settings for the semantic search system."""

import os
from pathlib import Path


class Config:
    """Configuration class for semantic search system."""
    
    # Qdrant settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "personal_notes")
    
    # Model settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-mpnet-base-v2")
    EMBEDDING_DIM: int = 768
    
    # Text processing settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    MAX_WORDS_BEFORE_CHUNKING: int = int(os.getenv("MAX_WORDS_BEFORE_CHUNKING", "1000"))
    
    # Indexing settings
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "32"))
    
    # API settings
    FLASK_HOST: str = os.getenv("FLASK_HOST", "localhost")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # File paths
    NOTES_DIR: Path = Path(os.getenv("NOTES_DIR", "./notes"))
    SUPPORTED_EXTENSIONS: list[str] = ["*.txt", "*.md", "*.org"]
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        if not cls.NOTES_DIR.exists():
            raise ValueError(f"Notes directory does not exist: {cls.NOTES_DIR}")
        
        if cls.CHUNK_SIZE <= cls.CHUNK_OVERLAP:
            raise ValueError("CHUNK_SIZE must be greater than CHUNK_OVERLAP")
        
        if cls.EMBEDDING_DIM <= 0:
            raise ValueError("EMBEDDING_DIM must be positive")


# Global config instance
config = Config()