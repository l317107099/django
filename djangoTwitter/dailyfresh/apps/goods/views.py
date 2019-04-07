from django.shortcuts import render,redirect
from django.urls import reverse
from goods.models import *
from django.views.generic import View
from django.core.cache import cache
from django.contrib.auth import authenticate
from django_redis import get_redis_connection
from django.core.paginator import Paginator
# Create your views here.

class IndexView(View):
    '''首页'''
    def get(self,request):
        '''显示首页'''
        # 尝试从缓存中获取数据
        # return render(request,'index.html')

        context = cache.get('index_page_data')

        if context is None:
            print('设置缓存')
            # 缓存中没有数据
            # 获取商品的种类信息
            types = GoodsType.objects.all()

            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            # 获取首页促销活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            for type in types: # GoodsType
                # 获取type种类首页分类商品的图片展示信息

                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                # 获取type种类首页分类商品的文字展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                type.image_banners = image_banners
                type.title_banners = title_banners

            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners,
                       }
            # 设置缓存
            # key  value timeout
            # cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 1
        # print(cart_count)
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context.update(cart_count=cart_count)

        # 使用模板
        return render(request, 'index.html', context)


class DetailView(View):
    def get(self,request,goods_id):
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取商品的评论信息
        # sku_orders = OrdeGoo
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
        # 获取同一个SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
        user =request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            #
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)
        context = {'sku': sku, 'types': types,
                   'new_skus': new_skus,
                   'same_spu_skus': same_spu_skus,
                   'cart_count': cart_count,
                   'same_spu_skus':same_spu_skus
                   }
        return render(request,'detail.html',context)


class ListView(View):
    def get(self, request, type_id, page):
        try:
            type=GoodsType.objects.get(id=type_id)
        except:
            return redirect(reverse('goods:index'))
        types=GoodsType.objects.all()
        sort=request.GET.get('sort')
        if sort ==' price':
            skus=GoodsSKU.objects.filter(type=type).order_by('price')

        elif sort == 'hot':
            skus=GoodsSKU.objects.filter(type=type).order_by('-sales')

        else:
            sort == 'default'
            skus=GoodsSKU.objects.filter(type=type).order_by('-id')

        paginator=Paginator(skus,1)

        try:
            page=int(page)

        except Exception as e:
            page=1
        if page > paginator.num_pages:
            page=1

        skus_page=paginator.page(page)

        num_pages=paginator.num_pages
        if num_pages<5:
            pages=range(1,num_pages+1)
        elif page<=3:
            pages=range(1,6)
        elif num_pages-page<=2:
            pages=range(num_pages-4,num_pages+1)
        else:
            pages=range(page-2,page+3)

        new_skus=GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]
        user=request.user
        cart_count=0
        if user.is_authenticated:
            conn=get_redis_connection('default')
            cart_key='cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

        context={
            'type':type,
            'types':types,
            'skus_page':skus_page,
            'new_skus':new_skus,
            'cart_count':cart_count,
            'pages':pages,
            'sort':sort
        }

        return render(request,'list.html',context)