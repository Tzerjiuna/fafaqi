from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductImage,
    Order, OrderItem, OrderMessage
)

# 基本模型注册
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductImage)

# 订单商品 inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'get_total')

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Total Price"

# 订单消息 inline
class OrderMessageInline(admin.TabularInline):
    model = OrderMessage
    extra = 1  # 默认显示1行可填写
    fields = ('sender', 'message', 'timestamp')
    readonly_fields = ('sender', 'timestamp')
    can_delete = False

# 订单管理
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'payment_status', 'total_price')
    list_filter = ('status', 'payment_status')
    search_fields = ('id', 'customer__user__username', 'customer__user__email')
    inlines = [OrderItemInline, OrderMessageInline]
    readonly_fields = ('total_price',)

# 独立消息管理（可选）
@admin.register(OrderMessage)
class OrderMessageAdmin(admin.ModelAdmin):
    list_display = ('order', 'sender', 'short_message', 'timestamp')
    search_fields = ('order__id', 'sender__username', 'message')
    list_filter = ('timestamp',)

    def short_message(self, obj):
        return obj.message[:40] + '...' if len(obj.message) > 40 else obj.message
    short_message.short_description = 'Message'
