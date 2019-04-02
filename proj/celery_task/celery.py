from celery import Celery

cel = Celery(
    broker='redis://172.96.198.74:6379/1',
    backend='redis://172.96.198.74:6379/2',
    include=[
        'celery_task.emails',
        'celery_task.order_expired'
    ]
)

cel.conf.timezone = 'Asia/Shanghai'
cel.conf.enable_utc = False
