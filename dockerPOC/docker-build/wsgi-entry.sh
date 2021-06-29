#!/bin/bash

exec gunicorn BackendApp.wsgi:application --preload --bind 0.0.0.0:8000 -w 3 --threads 10 -t 50 --access-logfile=/rest/logs/gunicorn.log  --error-logfile=/rest/logs/gunicorn.log --log-file=/rest/logs/gunicorn.log   "$@"
