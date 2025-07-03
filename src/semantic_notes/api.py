"""Flask API for semantic search functionality."""

from flask import Flask, request, jsonify, send_file
from typing import Dict, Any
import logging
import os
from pathlib import Path

from .config import config
from .vector_store import vector_store
from .models import SearchResponse

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Enable CORS for frontend development
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    @app.route('/search', methods=['GET', 'POST'])
    def search_endpoint():
        """Search endpoint for semantic search queries."""
        try:
            # Parse request parameters
            if request.method == 'GET':
                query = request.args.get('q', '')
                limit = int(request.args.get('limit', 10))
            else:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Invalid JSON in request body'}), 400
                query = data.get('query', '')
                limit = data.get('limit', 10)
            
            # Validate parameters
            if not query:
                return jsonify({'error': 'Query parameter is required'}), 400
            
            if limit <= 0 or limit > 100:
                return jsonify({'error': 'Limit must be between 1 and 100'}), 400
            
            # Perform search
            results = vector_store.search(query, limit)
            
            # Create response
            response = SearchResponse(
                query=query,
                results=results,
                count=len(results),
                limit=limit
            )
            
            return jsonify(response.to_dict())
        
        except ValueError as e:
            return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
        except Exception as e:
            logger.error(f"Search error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            # Test vector store connection
            info = vector_store.get_collection_info()
            return jsonify({
                'status': 'healthy',
                'collection': info.model_dump() if hasattr(info, 'model_dump') else str(info)
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 503
    
    @app.route('/info', methods=['GET'])
    def info_endpoint():
        """Get information about the search system."""
        try:
            collection_info = vector_store.get_collection_info()
            return jsonify({
                'model_name': config.MODEL_NAME,
                'collection_name': config.COLLECTION_NAME,
                'embedding_dim': config.EMBEDDING_DIM,
                'collection_info': collection_info.model_dump() if hasattr(collection_info, 'model_dump') else str(collection_info)
            })
        except Exception as e:
            logger.error(f"Info endpoint error: {e}")
            return jsonify({'error': 'Could not retrieve system information'}), 500

    @app.route('/file', methods=['GET'])
    def file_endpoint():
        """Serve file content for viewing."""
        try:
            file_path = request.args.get('path')
            if not file_path:
                return jsonify({'error': 'File path parameter is required'}), 400
            
            # Resolve the full path
            full_path = Path(file_path).resolve()
            
            # Security check: ensure the file is within notes directory
            notes_dir = Path(config.NOTES_DIR).resolve()
            try:
                full_path.relative_to(notes_dir)
            except ValueError:
                return jsonify({'error': 'Access denied: file outside notes directory'}), 403
            
            # Check if file exists
            if not full_path.exists():
                return jsonify({'error': 'File not found'}), 404
            
            # Check if it's a file (not directory)
            if not full_path.is_file():
                return jsonify({'error': 'Path is not a file'}), 400
            
            # Read and return file content as text
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
            except UnicodeDecodeError:
                return jsonify({'error': 'File is not a text file or has encoding issues'}), 400
            
        except Exception as e:
            logger.error(f"File endpoint error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


def run_server(host: str = None, port: int = None, debug: bool = None) -> None:
    """Run the Flask development server.
    
    Args:
        host: Host to bind to (default from config)
        port: Port to bind to (default from config)  
        debug: Enable debug mode (default from config)
    """
    app = create_app()
    app.run(
        host=host or config.FLASK_HOST,
        port=port or config.FLASK_PORT,
        debug=debug if debug is not None else config.FLASK_DEBUG
    )