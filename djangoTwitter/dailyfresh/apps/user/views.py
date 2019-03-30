from django.shortcuts import render,reverse,redirect,HttpResponse
# from django.contrib.auth.models import User
from user.models import *
from django.views import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
from celery_tasks.tasks import send_register_active
from django.contrib.auth import authenticate,login
from django_redis import get_redis_connection
from django.contrib.auth.decorators import login_required
from time import sleep
from django.core.mail import send_mail
from goods.models import GoodsSKU
from utils.mixin import LoginRequiredMixin
# Create your views here.
# def register(requeset):

class RegisterView(View):
    def get(self,requeset):
        return render(requeset, 'register.html')
    def post(self,requeset):
        _userinfo = {
            'user_name': '',
            'pwd': '',
            'cpwd': '',
            'email': '',
            'allow': '',

        }
        try:
            _userinfo = {
                'user_name': requeset.POST['user_name'],
                'pwd': requeset.POST['pwd'],
                'email': requeset.POST['email'],
                'allow': requeset.POST['allow'],
                'cpwd': requeset.POST['cpwd'],
            }

            is_post = True
        except (KeyError):
            is_post = False

        if is_post:
            states = do_sigup(requeset, _userinfo)

        if states['success']:
            users = User.objects.create_user(_userinfo['user_name'], _userinfo['email'], _userinfo['pwd'])
            users.is_active = 0
            users.save()
            sec_key=Serializer(settings.SECRET_KEY,3600)
            keys={'config':users.id}
            # str(keys,encoding="utf-8")
            token=sec_key.dumps(keys) #bytes

            token=token.decode() #'\x00'
            # subject='天天生鲜'
            # message=''
            # from_email=settings.EMAIL_FROM
            # recv=[_userinfo['email']]

            # jh='<h1>{0}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{1}">http://127.0.0.1:8000/user/active/{2}</a>' .format(_userinfo['user_name'], token, token)

            # send_mail(subject=subject,message=message,from_email=from_email,recipient_list=recv,html_message=jh)

            send_register_active.delay(_userinfo['email'],_userinfo['user_name'],token)

            # sleep(20)
            return redirect(reverse('goods:index'))
        else:
            result = {
                'success': states['success'],
                'message': states['message']
            }

            return render(requeset, 'register.html', {'message': result['message']})

class ActiveView(View):

    def get(self,request,token):
        sec_key = Serializer(settings.SECRET_KEY, 3600)
        try:
            info=sec_key.loads(token)
            user_id=info['config']
            user=User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('goods:index'))
        except SignatureExpired as e:
        # 激活链接已过期
            return HttpResponse('激活链接已过期')

def register(requeset):
    if requeset.method =='GET':

        return render(requeset, 'register.html')

    else:

        _userinfo={
            'user_name':'',
            'pwd':'',
            'cpwd':'',
            'email':'',
            'allow':'',

        }
        try :
            _userinfo ={
                'user_name':requeset.POST['user_name'],
                'pwd': requeset.POST['pwd'],
                'email': requeset.POST['email'],
                'allow': requeset.POST['allow'],
                'cpwd': requeset.POST['cpwd'],
            }

            is_post=True
        except (KeyError):
            is_post=False

        if is_post:
            states=do_sigup(requeset,_userinfo)

        if states['success']:
            return redirect(reverse('goods:index'))
        else:
            result={
                'success':states['success'],
                'message':states['message']
            }

            return render(requeset,'register.html',{'message':result['message']})

        # user=User.objects.create_user(user_name,pwd,email,allow)
        # user.save()

def do_sigup(requset,_userinfo):
    states={
        'success':False,
        'message':''
    }

    if _userinfo['user_name']=='':
        states['success']=False
        states['message']="用户名不能为空"
        return states
    if _userinfo['user_name']:

        user= User.objects.filter(username=_userinfo['user_name'])
        if user:
            states['success'] = False
            states['message'] = '用户名已经注册'
            return states


    if _userinfo['pwd']=='':
        states['success']=False
        states['message']='用户密码不能为空'
        return states

    if _userinfo['pwd'] != _userinfo['cpwd']:
        states['success'] = False
        states['message'] = '两次输入的密码不一致'
        return states

    if _userinfo['allow'] != 'on':
        states['success'] = False
        states['message'] = '请浏览协议'
        return states

    #1582788117@qq.com/1582788117@163.com
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',_userinfo['email']):
        states['success']=False
        states['message']='输入的邮箱格式不正确'
        return states


    # user = User.objects.create_user(username, email, password)
    # users=User.objects.create_user(_userinfo['user_name'],_userinfo['email'],_userinfo['pwd'])
    # users.is_active = 0
    # users.save()

    states['success']=True
    return states

# 登陆
class loginView(View):
    def get(self,request):
        if 'username' in request.COOKIES:
            username=request.COOKIES.get('username')
            checked='checked'
        else:
            username=''
            checked=''
        return render(request,'login.html',{'username':username,'checked':checked})
    def post(self,request):
        username=request.POST['username']
        password=request.POST['pwd']

        user=authenticate(username=username,password=password)
        if not all([username,password]):
            return render(request,'login.html',{'message':'数据不完整'})
        if user is not None:
            if user.is_active:
                login(request,user)
                next_url=request.GET.get('next',reverse('goods:index'))
                remenber = request.POST.get('remenber')
                response=redirect(next_url)
                if remenber == 'on':

                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                return response
            else:
                return render(request,'login.html',{'message':'用户未激活'})
        else:
            return render(request,'login.html',{'message':'用户名或密码错误'})



class userInfoView(LoginRequiredMixin,View):
    def get(self,request):
        "request.user.is_authenticated()"
        user=request.user
        user_message=Address.objects.get_default_address(user)

        con=get_redis_connection('default')
        history_key='history_{0}'.format(user.id)
        skus=con.lrange(history_key,0,4)
        sku_list=[]
        for sku in skus:
            goods=GoodsSKU.objects.get(id=sku)
            sku_list.append(goods)

        context = {
                   'message':user_message,
                   'goods_li': sku_list}

        return  render(request,'user_center_info.html',context)
    def post(self,request):
        pass

class userOrderView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'user_center_order.html')
    def post(self,request):
        pass

# class userSiteView(LoginRequiredMixin,View):
#     def get(self,request):
#         return render(request,'user_center_site.html')

class userSiteView(LoginRequiredMixin,View):
    def get(self,request):

        user = request.user
        # 添加新的收货地址
        # try:
        #     adds = Address.objects.get(user=user, is_default=True)
        # except:
        #     adds = None
        adds=Address.objects.get_default_address(user)

        return render(request,'user_center_site.html',{'message':adds})

    def post(self,request):
        receiver=request.POST.get('recevicer')
        addr=request.POST.get('addr')
        zip_code=request.POST.get('zip_code')
        phon=request.POST.get('phon')
        if not all([receiver,addr,phon]):
            return render(request,'user_center_site.html',{'message':'数据不完整'})

        if not re.match('^1[3|4|5|7|8][0-9]{9}$',phon):
            return render(request,'user_center_site.html',{'message':'手机格式不正确'})

        user=request.user
        #添加新的收货地址
        # try:
        #     adds=Address.objects.get(user=user,is_default=True)
        # except:
        #     adds=None
        adds = Address.objects.get_default_address(user)
        if adds:
           is_default=False
        else:
            is_default=True

        Address.objects.create(
            user=user,
            receiver=receiver,
            addr=addr,
            zip_code=zip_code,
            phone=phon,
            is_default=is_default
        )

        return redirect(reverse('user:site'))


