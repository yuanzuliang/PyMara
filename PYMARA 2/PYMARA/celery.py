from celery import Celery
from django.conf import settings
import os

# 为celery设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PYMARA.settings')

# 创建应用
app = Celery("update_blog_history")
# 配置应用
app.conf.update(
    # 配置broker
    BROKER_URL='redis://:@127.0.0.1:6379/8',
)
# 设置app自动加载任务
app.autodiscover_tasks(settings.INSTALLED_APPS)
# app.autodiscover_tasks('Public.task')
