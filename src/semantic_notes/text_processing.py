"""Text processing utilities for chunking and preparing documents."""

from pathlib import Path
from typing import List
import re

from .config import config
from .models import DocumentChunk


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks by word count.
    
    Args:
        text: The text to chunk
        chunk_size: Number of words per chunk (default from config)
        overlap: Number of words to overlap between chunks (default from config)
    
    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP
    
    # Clean and split text into words
    words = re.findall(r'\S+', text)
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if chunk_words:  # Skip empty chunks
            chunks.append(' '.join(chunk_words))
    
    return chunks


def should_chunk_file(word_count: int) -> bool:
    """Determine if a file should be chunked based on word count.
    
    Args:
        word_count: Number of words in the file
    
    Returns:
        True if file should be chunked, False otherwise
    """
    return word_count > config.MAX_WORDS_BEFORE_CHUNKING


def process_file(filepath: Path) -> List[DocumentChunk]:
    """Process a single file into chunks with metadata.
    
    Args:
        filepath: Path to the file to process
    
    Returns:
        List of DocumentChunk objects
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file can't be decoded as UTF-8
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Could not decode file {filepath} as UTF-8: {e}")
    
    word_count = len(content.split())
    
    # Decide whether to chunk
    if should_chunk_file(word_count):
        chunks = chunk_text(content)
    else:
        chunks = [content]
    
    # Create DocumentChunk objects
    results = []
    for i, chunk in enumerate(chunks):
        results.append(DocumentChunk(
            text=chunk,
            filepath=filepath,
            chunk_index=i,
            total_chunks=len(chunks),
            word_count=word_count,
            file_type=filepath.suffix
        ))
    
    return results


def find_note_files(notes_dir: Path = None, extensions: List[str] = None) -> List[Path]:
    """Find all note files in the specified directory.
    
    Args:
        notes_dir: Directory to search in (default from config)
        extensions: File extensions to search for (default from config)
    
    Returns:
        List of file paths
    """
    notes_dir = notes_dir or config.NOTES_DIR
    extensions = extensions or config.SUPPORTED_EXTENSIONS
    
    note_files = []
    for ext in extensions:
        note_files.extend(notes_dir.rglob(ext))
    
    return sorted(note_files)