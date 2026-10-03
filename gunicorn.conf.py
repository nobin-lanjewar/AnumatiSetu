"""
Gunicorn Production Server Configuration for AnumatiSetu
"""
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Calculate optimal workers based on CPU cores or environment override
default_workers = max(multiprocessing.cpu_count() * 2 + 1, 3)
workers = int(os.getenv("WEB_CONCURRENCY", default_workers))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = "gthread"

# Connection and timeout limits
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# Security and performance
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
