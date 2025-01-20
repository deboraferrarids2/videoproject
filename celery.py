from celery import Celery

# Set up the Celery app and configuration
app = Celery('videoproject')

# Configure Celery to use Redis as the broker (make sure Redis is running)
app.config_from_object('celery_config')

# Auto-discover tasks (so Celery knows where to look for them)
app.autodiscover_tasks(['app.tasks'])

# Optional: Configure the broker URL and backend (make sure Redis is running on the correct ports)
app.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/0'
)
