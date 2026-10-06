from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_price', 'shipping_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order_number', 'shipping_name', 'shipping_address', 'user__username')
    readonly_fields = ('order_number', 'user', 'total_price', 'created_at')
    inlines = [OrderItemInline]
