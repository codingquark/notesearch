"""Document indexing functionality."""

from pathlib import Path
from typing import List, Optional
import logging

from .config import config
from .text_processing import find_note_files, process_file
from .vector_store import vector_store
from .models import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Handles indexing of documents into the vector store."""
    
    def __init__(self, batch_size: int = None):
        """Initialize the indexer.
        
        Args:
            batch_size: Number of chunks to process in each batch
        """
        self.batch_size = batch_size or config.BATCH_SIZE
    
    def index_files(self, file_paths: List[Path], show_progress: bool = True) -> None:
        """Index a list of files.
        
        Args:
            file_paths: List of file paths to index
            show_progress: Whether to show progress information
        """
        # Ensure collection exists
        vector_store.ensure_collection_exists()
        
        all_chunks = []
        total_files = len(file_paths)
        
        for i, filepath in enumerate(file_paths):
            if show_progress and i % 10 == 0:
                logger.info(f"Processing file {i+1}/{total_files}: {filepath.name}")
            
            try:
                chunks = process_file(filepath)
                all_chunks.extend(chunks)
                
                # Index when batch is full
                if len(all_chunks) >= self.batch_size:
                    self._index_batch(all_chunks)
                    all_chunks = []
                    
            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")
                continue
        
        # Index remaining chunks
        if all_chunks:
            self._index_batch(all_chunks)
        
        if show_progress:
            logger.info("Indexing complete!")
    
    def _index_batch(self, chunks: List[DocumentChunk]) -> None:
        """Index a batch of chunks.
        
        Args:
            chunks: List of DocumentChunk objects to index
        """
        try:
            vector_store.index_chunks(chunks)
        except Exception as e:
            logger.error(f"Error indexing batch: {e}")
            raise
    
    def index_directory(self, 
                       notes_dir: Optional[Path] = None, 
                       extensions: Optional[List[str]] = None,
                       show_progress: bool = True) -> None:
        """Index all files in a directory.
        
        Args:
            notes_dir: Directory to index (default from config)
            extensions: File extensions to include (default from config)
            show_progress: Whether to show progress information
        """
        notes_dir = notes_dir or config.NOTES_DIR
        file_paths = find_note_files(notes_dir, extensions)
        
        if show_progress:
            logger.info(f"Found {len(file_paths)} files to index in {notes_dir}")
        
        self.index_files(file_paths, show_progress)
    
    def reindex_all(self, 
                   notes_dir: Optional[Path] = None,
                   extensions: Optional[List[str]] = None) -> None:
        """Delete existing collection and reindex all files.
        
        Args:
            notes_dir: Directory to index (default from config)
            extensions: File extensions to include (default from config)
        """
        logger.info("Deleting existing collection...")
        try:
            vector_store.delete_collection()
        except Exception as e:
            logger.warning(f"Could not delete collection (may not exist): {e}")
        
        logger.info("Starting fresh indexing...")
        self.index_directory(notes_dir, extensions)


# Global indexer instance
indexer = DocumentIndexer()