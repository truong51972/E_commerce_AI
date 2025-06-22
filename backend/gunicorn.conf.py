# gunicorn.conf.py
import multiprocessing
import os

bind = "0.0.0.0:8000"  # Bind address and port

# Determine the number of worker processes.
# If GUNICORN_WORKERS is set to "max", use (CPU cores * 2) + 1.
# Otherwise, use the value from the environment variable or default to 1.
if os.getenv("GUNICORN_WORKERS") == "max":
    workers = multiprocessing.cpu_count() * 2 + 1
else:
    try:
        workers = int(os.getenv("GUNICORN_WORKERS"))
    except (TypeError, ValueError):
        workers = 1

# Determine the number of threads per worker.
# If GUNICORN_THREADS is set to "max", use (CPU cores * 2) + 1.
# Otherwise, use the value from the environment variable or default to 2.
if os.getenv("GUNICORN_THREADS") == "max":
    threads = multiprocessing.cpu_count() * 2 + 1
else:
    try:
        threads = int(os.getenv("GUNICORN_THREADS"))
    except (TypeError, ValueError):
        threads = 2

# Worker class for FastAPI (using UvicornWorker).
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts (in seconds).
timeout = 120  # Workers silent for more than this many seconds are killed and restarted
keepalive = 5  # The number of seconds to wait for requests on a Keep-Alive connection
graceful_timeout = 120  # Timeout for graceful workers restart

# Limit the number of requests a worker will process before restarting.
max_requests = 1000
max_requests_jitter = 200  # Random jitter to add to max_requests for each worker

# Buffer size (not used by UvicornWorker, but kept for compatibility).
worker_connections = 1000

# Logging configuration.
accesslog = "-"  # Log access to stdout
errorlog = "-"  # Log errors to stdout
loglevel = "info"  # Logging level

# Monitoring (uncomment to enable statsd).
# statsd_host = 'localhost:8125'
