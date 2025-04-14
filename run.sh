#!/bin/bash
poetry run watchmedo auto-restart -- -d /code/danboorutools -p="*" -R -- celery --app danboorutools.celery_tasks.tasks worker -B --loglevel=INFO -s /tmp/celerybeat-schedule --autoscale=10,1
