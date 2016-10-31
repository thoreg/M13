from celery.decorators import task
# from celery.task.schedules import crontab
from celery.utils.log import get_task_logger

from django.core import management

logger = get_task_logger(__name__)


# @periodic_task(
#     run_every=(crontab(minute='*/15')),
#     name="task_fetch_salesrank_and_price",
#     ignore_result=True
# )
@task
def task_fetch_salesrank_and_price():
    management.call_command('m13_get_salesrank', 'phantomjs')


# @periodic_task(
#     run_every=(crontab(minute='*/15')),
#     name="m13_aggregate_salesrankhistory",
#     ignore_result=True
# )
@task
def m13_aggregate_salesrankhistory():
    management.call_command('m13_aggregate_salesrankhistory')
