import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 讓 Celery 自動去所有已註冊的 Django app 中尋找名為 tasks.py 的檔案，並載入其中的任務
app.autodiscover_tasks()
