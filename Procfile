web: gunicorn jobtracker_backend_api.wsgi --log-file -
worker: celery -A jobtracker_backend_api worker --loglevel=info