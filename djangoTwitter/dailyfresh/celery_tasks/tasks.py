from celery import Celery
from django.core.mail import send_mail
from django.template import loader,RequestContext
import os
import time
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()
from goods.models import *
from dailyfresh import settings
from django_redis import get_redis_connection

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

@app.task
def send_register_active(to_email,username,token):
    subject='天天生鲜欢迎你'
    from_email= settings.EMAIL_FROM
    to_email=to_email
    message=''
    html_message='<h1>{0}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{1}">http://127.0.0.1:8000/user/active/{2}</a>' .format(username, token, token)
    send_mail(subject=subject,from_email=from_email,recipient_list=[to_email],message=message,html_message=html_message)
    time.sleep(5)

@app.task
def denerate_static_index_html():

    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    #
    # # 使用模板
    temp=loader.get_template('static_index.html')
    # context=RequestContext(request,context)
    # return render(request, 'index.html', context)
    static_index_html=temp.render(context)
    save_path=os.path.join(settings.BASE_DIR,'static/index.html')
    with open(save_path,'w') as f:
        f.write(static_index_html)