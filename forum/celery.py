import os
from celery import Celery

# Please note that you need to have Redis installed and the redis-server running for Celery to work. 
# Additionally, Celery was not functioning correctly for me until I installed eventlet (pip install eventlet) 
# Celery was giving a 'ValueError: not enough values to unpack (expected 3, got 0)' error when trying to call a task).
# After starting Redis, run the Celery worker with the command:
# celery -A forum worker -l INFO -P eventlet


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')

app = Celery('forum')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['forum'])


