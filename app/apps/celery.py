import os

from django.conf import settings

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.settings.production")

app = Celery("app_celery")
app.config_from_object(f"django.conf:{settings.__name__}", namespace="CELERY")
# Set autodiscovery
app.autodiscover_tasks()
