import os
from decimal import Decimal

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackendServer.settings')

app = Celery('BackendServer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
