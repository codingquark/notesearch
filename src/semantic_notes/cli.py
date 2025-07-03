"""Command-line interface for semantic search system."""

import argparse
import logging
import sys
from pathlib import Path

from .config import config
from .indexer import indexer
from .api import run_server


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def index_command() -> None:
    """CLI command for indexing documents."""
    parser = argparse.ArgumentParser(description='Index documents for semantic search')
    parser.add_argument(
        '--notes-dir', 
        type=Path,
        default=config.NOTES_DIR,
        help=f'Directory containing notes (default: {config.NOTES_DIR})'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=config.BATCH_SIZE,
        help=f'Batch size for indexing (default: {config.BATCH_SIZE})'
    )
    parser.add_argument(
        '--reindex',
        action='store_true',
        help='Delete existing collection and reindex all files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    try:
        # Validate configuration
        config.validate()
        
        # Update notes directory if provided
        if args.notes_dir != config.NOTES_DIR:
            config.NOTES_DIR = args.notes_dir
        
        # Update batch size if provided
        if args.batch_size != config.BATCH_SIZE:
            config.BATCH_SIZE = args.batch_size
            indexer.batch_size = args.batch_size
        
        # Perform indexing
        if args.reindex:
            indexer.reindex_all()
        else:
            indexer.index_directory()
            
    except Exception as e:
        logging.error(f"Indexing failed: {e}")
        sys.exit(1)


def serve_command() -> None:
    """CLI command for running the search server."""
    parser = argparse.ArgumentParser(description='Run semantic search API server')
    parser.add_argument(
        '--host',
        default=config.FLASK_HOST,
        help=f'Host to bind to (default: {config.FLASK_HOST})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=config.FLASK_PORT,
        help=f'Port to bind to (default: {config.FLASK_PORT})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    try:
        # Validate configuration
        config.validate()
        
        logging.info(f"Starting server on {args.host}:{args.port}")
        run_server(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Semantic search for personal notes')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index documents')
    index_parser.set_defaults(func=index_command)
    
    # Serve command  
    serve_parser = subparsers.add_parser('serve', help='Run API server')
    serve_parser.set_defaults(func=serve_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func()


if __name__ == '__main__':
    main()