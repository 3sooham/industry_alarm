# Create your tasks here
from celery import shared_task
import account.views

@shared_task(name='my_task')
def my_task(user_id):
     pass