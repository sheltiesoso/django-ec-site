from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('complete/<str:order_number>/', views.order_complete, name='order_complete'),
    path('history/', views.order_history, name='order_history'),
    path('history/<str:order_number>/', views.order_detail, name='order_detail'),
]
