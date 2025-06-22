# gunicorn.conf.py
import multiprocessing
import os

bind = "0.0.0.0:8000"

# number of worker processes
if os.getenv("GUNICORN_WORKERS") == "max":
    workers = multiprocessing.cpu_count() * 2 + 1
else:
    try:
        workers = int(os.getenv("GUNICORN_WORKERS"))
    except:
        workers = 1

if os.getenv("GUNICORN_THREADS") == "max":
    threads = multiprocessing.cpu_count() * 2 + 1
else:
    try:
        threads = int(os.getenv("GUNICORN_THREADS"))
    except:
        threads = 2

# reload = True
# Worker class
worker_class = "uvicorn.workers.UvicornWorker"

# threads for worker


# Timeouts
timeout = 120
keepalive = 5
graceful_timeout = 120

# limit requests
max_requests = 1000
max_requests_jitter = 200

# Buffer size
worker_connections = 1000

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"


# Monitoring
# statsd_host = 'localhost:8125'
