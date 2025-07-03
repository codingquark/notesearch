# Semantic Search Notes

A semantic search system for personal notes using vector embeddings and Qdrant vector database.

## Features

- **Semantic Search**: Find notes by meaning, not just keywords
- **Multiple Formats**: Supports `.txt`, `.md`, and `.org` files
- **Smart Chunking**: Automatically chunks large documents for better search
- **REST API**: HTTP API for integration with other tools
- **CLI Interface**: Command-line tools for indexing and serving
- **Production Ready**: Includes deployment configuration

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Qdrant vector database running on localhost:6333

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd semantic_search_notes_v1
```

2. Install the package:
```bash
# For basic usage
pip install -e .

# For development
pip install -e ".[dev]"
```

3. Set up your notes directory:
```bash
export NOTES_DIR="/path/to/your/notes"
```

### Usage

#### 1. Index your notes:
```bash
semantic-notes-index --notes-dir ./notes
```

#### 2. Start the search server:
```bash
semantic-notes-serve
```

#### 3. Search your notes:
```bash
curl "http://localhost:5000/search?q=productivity&limit=5"
```

## Configuration

The system can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTES_DIR` | `./notes` | Directory containing your notes |
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `MODEL_NAME` | `all-mpnet-base-v2` | Sentence transformer model |
| `CHUNK_SIZE` | `500` | Words per chunk for large documents |
| `FLASK_HOST` | `localhost` | API server host |
| `FLASK_PORT` | `5000` | API server port |

## Development

### Setup Development Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/semantic_notes

# Run specific test file
pytest tests/test_config.py
```

## Deployment

### Using Systemd (Linux)

1. Copy the service file:
```bash
sudo cp deployment/semantic_search.service /etc/systemd/system/
```

2. Start the service:
```bash
sudo systemctl enable semantic_search
sudo systemctl start semantic_search
```

### Using Docker

```bash
# Build image
docker build -t semantic-search-notes .

# Run container
docker run -d -p 5000:5000 \
  -v /path/to/notes:/app/notes \
  -e NOTES_DIR=/app/notes \
  semantic-search-notes
```

### Using Gunicorn

```bash
gunicorn -c deployment/gunicorn.conf.py semantic_notes.api:create_app
```

## Performance Considerations

- **Model Loading**: The sentence transformer model is loaded lazily and cached
- **Batch Processing**: Documents are indexed in configurable batches
- **Memory Usage**: Consider using CPU-only FAISS for lower memory usage
- **Scaling**: Use multiple Gunicorn workers for higher throughput (GPU setups may need single worker)

## Troubleshooting

### Common Issues

1. **Qdrant Connection Error**: Ensure Qdrant is running on the configured host/port
2. **Model Download**: First run may be slow due to model download
3. **Memory Issues**: Consider reducing batch size or using smaller models
4. **GPU Issues**: Check CUDA compatibility and install appropriate PyTorch version

### Logging

Enable verbose logging:
```bash
semantic-notes-serve --verbose
```

## License

MIT License - see LICENSE file for details.