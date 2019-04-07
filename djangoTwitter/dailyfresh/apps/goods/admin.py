from django.contrib import admin
from goods.models import IndexGoodsBanner,IndexTypeGoodsBanner,IndexPromotionBanner,GoodsType,GoodsSKU,Goods
# Register your models here.
class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from celery_tasks.tasks import denerate_static_index_html
        denerate_static_index_html.delay()

    def delete_model(self, request, obj):
        super().delete_model(self, request, obj)
        from celery_tasks.tasks import denerate_static_index_html
        denerate_static_index_html.delay()

class GoodsTypeAdmin(BaseAdmin):
    pass

class IndexTypesAdmin(BaseAdmin):
    pass

class IndexGoodsAdmin(BaseAdmin):
    pass
class IndexPromotionsAdmin(BaseAdmin):
    pass

class GoodsSKUAdmin(BaseAdmin):
    pass

class GoodsAdmin(BaseAdmin):
    pass
admin.site.register(GoodsType,GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsAdmin)
admin.site.register(IndexTypeGoodsBanner,IndexTypesAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionsAdmin)
admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(Goods,GoodsAdmin)