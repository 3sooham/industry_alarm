import os

from celery import Celery
from account.tasks import temp_task

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# on_after_finalize

# @app.on_after_configure.connect

@app.on_after_finalize
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.

    # Setting these up from within the on_after_configure handler means that
    # we’ll not evaluate the app at module level when using test.s()
    sender.add_periodic_task(10.0, temp_task.s(1, 2), name='add every 10')


@app.task
def test(x, y):
    return x + y
