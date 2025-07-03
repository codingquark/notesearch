"""Embedding generation utilities using sentence transformers."""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import config


class EmbeddingModel:
    """Wrapper around SentenceTransformer for generating embeddings."""
    
    def __init__(self, model_name: str = None):
        """Initialize the embedding model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name or config.MODEL_NAME
        self._model: Optional[SentenceTransformer] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy loading of the sentence transformer model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def encode(self, texts: List[str], show_progress_bar: bool = False) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to encode
            show_progress_bar: Whether to show progress bar during encoding
        
        Returns:
            Array of embeddings with shape (len(texts), embedding_dim)
        """
        return self.model.encode(texts, show_progress_bar=show_progress_bar)
    
    def encode_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text.
        
        Args:
            text: Text to encode
        
        Returns:
            Single embedding vector
        """
        return self.model.encode([text])[0]
    
    @property
    def embedding_dim(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.model.get_sentence_embedding_dimension()


# Global embedding model instance
embedding_model = EmbeddingModel()