from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns  # 导入 i18n_patterns
from django.views.i18n import set_language  # 导入 set_language 视图
from core import views
from django.contrib.auth.views import LogoutView
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
]

# 用 i18n_patterns 包裹所有需要国际化的路径
urlpatterns += i18n_patterns(
    path('', views.home, name='home'),
    path('set-language/', set_language, name='set_language'),  # 设置语言切换路由
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search, name='search'),
    path('sale/', views.sale, name='sale'),
    path('new-in/', views.new_in, name='new_in'),
    path('brands/', views.brands, name='brands'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<slug:slug>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('auth/', views.CustomLoginView.as_view(), name='login'),
    path('auth/register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('order/<int:order_id>/chat/', views.order_chat, name='order_chat'),
)
