from celery import Celery
from django.core.mail import send_mail
from dailyfresh import settings
import os
import django
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

@app.task
def send_register_active(to_email,username,token):
    subject='天天生鲜欢迎你'
    from_email=settings.EMAIL_FROM
    to_email=to_email
    message=''
    html_message='<h1>{0}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{1}">http://127.0.0.1:8000/user/active/{2}</a>' .format(username, token, token)
    send_mail(subject=subject,from_email=from_email,recipient_list=[to_email],message=message,html_message=html_message)
    time.sleep(5)