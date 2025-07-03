"""Data models and utilities for the semantic search system."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document."""
    text: str
    filepath: Path
    chunk_index: int
    total_chunks: int
    word_count: int
    file_type: str
    
    @property
    def filename(self) -> str:
        """Get the filename without path."""
        return self.filepath.name
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata as a dictionary."""
        return {
            'filepath': str(self.filepath),
            'filename': self.filename,
            'chunk_index': self.chunk_index,
            'total_chunks': self.total_chunks,
            'word_count': self.word_count,
            'file_type': self.file_type
        }
    
    def get_point_id(self) -> str:
        """Generate a deterministic point ID for this chunk."""
        return str(uuid.uuid5(
            uuid.NAMESPACE_DNS, 
            f"{self.filepath}_{self.chunk_index}"
        ))


@dataclass
class SearchResult:
    """Represents a search result."""
    filepath: str
    best_score: float
    hits: int
    filename: Optional[str] = None
    
    def __post_init__(self):
        if self.filename is None:
            self.filename = Path(self.filepath).name


@dataclass
class SearchResponse:
    """Represents the response from a search query."""
    query: str
    results: List[SearchResult]
    count: int
    limit: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'query': self.query,
            'results': [
                {
                    'filepath': r.filepath,
                    'filename': r.filename,
                    'best_score': r.best_score,
                    'hits': r.hits
                }
                for r in self.results
            ],
            'count': self.count,
            'limit': self.limit
        }