"""Tests for configuration module."""

import pytest
from pathlib import Path
import tempfile

from semantic_notes.config import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    
    assert config.QDRANT_HOST == "localhost"
    assert config.QDRANT_PORT == 6333
    assert config.COLLECTION_NAME == "personal_notes"
    assert config.MODEL_NAME == "all-mpnet-base-v2"
    assert config.EMBEDDING_DIM == 768


def test_config_validation_valid():
    """Test configuration validation with valid settings."""
    config = Config()
    
    # Create temporary notes directory
    with tempfile.TemporaryDirectory() as tmpdir:
        config.NOTES_DIR = Path(tmpdir)
        config.validate()  # Should not raise


def test_config_validation_missing_notes_dir():
    """Test configuration validation with missing notes directory."""
    config = Config()
    config.NOTES_DIR = Path("/nonexistent/directory")
    
    with pytest.raises(ValueError, match="Notes directory does not exist"):
        config.validate()


def test_config_validation_invalid_chunk_settings():
    """Test configuration validation with invalid chunk settings."""
    config = Config()
    config.CHUNK_SIZE = 100
    config.CHUNK_OVERLAP = 200  # Overlap greater than chunk size
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config.NOTES_DIR = Path(tmpdir)
        with pytest.raises(ValueError, match="CHUNK_SIZE must be greater than CHUNK_OVERLAP"):
            config.validate()