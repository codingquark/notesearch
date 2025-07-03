# Gunicorn configuration for semantic search Flask app
bind = "127.0.0.1:5000"
workers = 1  # Single worker to avoid multiple model instances
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True  # Load the app before forking workers
reload = False  # Disable auto-reload in production

# Application module
module = "semantic_notes.api:create_app()"

# Process naming
proc_name = "semantic-search-notes"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 