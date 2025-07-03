"""Vector store operations using Qdrant."""

from typing import List, Optional
from collections import defaultdict

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from .config import config
from .models import DocumentChunk, SearchResult
from .embeddings import embedding_model


class VectorStore:
    """Vector store for managing document embeddings in Qdrant."""
    
    def __init__(self, host: str = None, port: int = None, collection_name: str = None):
        """Initialize the vector store.
        
        Args:
            host: Qdrant host (default from config)
            port: Qdrant port (default from config)
            collection_name: Collection name (default from config)
        """
        self.host = host or config.QDRANT_HOST
        self.port = port or config.QDRANT_PORT
        self.collection_name = collection_name or config.COLLECTION_NAME
        self._client: Optional[QdrantClient] = None
    
    @property
    def client(self) -> QdrantClient:
        """Lazy loading of Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(host=self.host, port=self.port)
        return self._client
    
    def ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create if it doesn't."""
        collections = self.client.get_collections().collections
        if not any(col.name == self.collection_name for col in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=config.EMBEDDING_DIM, 
                    distance=Distance.COSINE
                )
            )
    
    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Index a batch of document chunks.
        
        Args:
            chunks: List of DocumentChunk objects to index
        """
        if not chunks:
            return
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_model.encode(texts, show_progress_bar=True)
        
        # Create points for Qdrant
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                PointStruct(
                    id=chunk.get_point_id(),
                    vector=embedding.tolist(),
                    payload=chunk.metadata
                )
            )
        
        # Upsert to Qdrant
        self.client.upsert(collection_name=self.collection_name, points=points)
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for similar documents.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
        
        Returns:
            List of SearchResult objects
        """
        # Generate query embedding
        query_vector = embedding_model.encode_single(query).tolist()
        
        # Search in Qdrant (get more results to group by file)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit * 3
        )
        
        # Group results by file and get best score per file
        files_scores = defaultdict(list)
        for hit in results:
            filepath = hit.payload['filepath']
            files_scores[filepath].append(hit.score)
        
        # Create SearchResult objects
        file_results = []
        for filepath, scores in files_scores.items():
            file_results.append(SearchResult(
                filepath=filepath,
                best_score=max(scores),
                hits=len(scores)
            ))
        
        # Sort by best score and limit results
        file_results.sort(key=lambda x: x.best_score, reverse=True)
        return file_results[:limit]
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(collection_name=self.collection_name)
    
    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        return self.client.get_collection(collection_name=self.collection_name)


# Global vector store instance
vector_store = VectorStore()