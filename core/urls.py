from django.urls import path
from core import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
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
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('auth/', views.CustomLoginView.as_view(), name='login'),
    path('auth/register/', views.register, name='register'),  # Separate path for clarity
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('order/<int:order_id>/chat/', views.order_chat, name='order_chat'),

]

urlpatterns += i18n_patterns(
    path('set-language/', views.set_language, name='set_language'),  # This is for language switching
    # You can add other i18n specific URL patterns here if needed
)