from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),  # تسجيل خروج المستخدم العادي
    path('register/', views.register, name='register'),
    path('order-success/', views.order_success, name='order_success'),
]
