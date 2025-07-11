# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# 確保在其他地方使用 @shared_task 裝飾器時，任務會被正確地註冊到我們剛剛建立的 Celery app 上。

from .celery import app as celery_app

__all__ = ('celery_app',)
