# celery_utils.py
from celery import Celery

def make_celery(app_name=__name__):
    celery_app = Celery(
        app_name,
        broker='redis://redis:6379/0',
        backend='redis://redis:6379/0',
    )
    celery_app.autodiscover_tasks(['app'])
    return celery_app

# Exponha a instância do Celery como `celery`
celery = make_celery()
