from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Category, Brand, Product, Customer, Order, OrderItem, Wishlist
from django.http import HttpResponseRedirect
from django.contrib import messages
import stripe
from django.contrib import admin


from core import views
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.urls import path
from django.conf.urls.i18n import i18n_patterns

from django.views.i18n import set_language

# from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
stripe.api_key = settings.STRIPE_SECRET_KEY
from core import views

class CustomLoginView(LoginView):
    template_name = 'auth.html'
    redirect_authenticated_user = True

    def get_credentials(self):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        user = User.objects.filter(email__iexact=username).first()
        return {'username': user.username if user else username, 'password': password}

    def form_valid(self, form):
        credentials = self.get_credentials()
        user = authenticate(**credentials)
        if user:
            form.cleaned_data['username'] = credentials['username']
            return super().form_valid(form)
        form.add_error(None, _("邮箱或密码错误"))
        return self.form_invalid(form)





def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, _("两次输入的密码不一致"))
            return render(request, 'auth.html', {'signup_active': True})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, _("用户名已被使用。"))
            return render(request, 'auth.html', {'signup_active': True})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, _("邮箱已被注册。"))
            return render(request, 'auth.html', {'signup_active': True})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        Customer.objects.create(
            user=user,
            phone='',
            address=''
        )
        messages.success(request, "Account created successfully! Please sign in.")
        return render(request, 'auth.html', {'signup_active': False})
    return render(request, 'auth.html', {'signup_active': True})


def home(request):
    categories = Category.objects.filter(name__in=['Women', 'Men', 'Kids'])
    all_categories = Category.objects.all()
    context = {
        'main_categories': categories,
        'categories': all_categories,
    }
    return render(request, 'index.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(categories=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'product_list.html', context)


def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brand=brand)
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {
        'product': product,
    }
    return render(request, 'product_detail.html', context)


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if not product.in_stock:
        messages.error(request, _("该商品已售罄。"))
        return redirect('product_detail', slug=slug)

    customer, created = Customer.objects.get_or_create(user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    quantity = int(request.POST.get('quantity', 1))
    
    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    order.calculate_total()

    messages.success(request, _("%(product)s 已加入购物车！") % {'product': product.title})
    return redirect('cart')

@login_required
def cart(request):
    customer = get_object_or_404(Customer, user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order.calculate_total()
    context = {
        'order': order,
        'order_total': order.total_price,
    }
    return render(request, 'cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    if order_item.order.customer.user == request.user:
        order_item.delete()
        order_item.order.calculate_total()
        messages.success(request, "Item removed from your cart.")
    return redirect('cart')

@login_required
def checkout(request):
    customer = get_object_or_404(Customer, user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    if request.method == 'POST':
        # 获取表单数据
        customer.phone = request.POST['phone']
        customer.address = request.POST['address']
        customer.name = request.POST['name']
        customer.bank_account = request.POST['bank_account']
        customer.bank_name = request.POST['bank_name']
        customer.save()

        # 如果没填银行信息，退回购物车
        if not customer.bank_account or not customer.bank_name:
            messages.error(request, "Please enter your bank account and bank name before placing the order.")
            return redirect('cart')

        # 计算订单
        order.distance_km = float(request.POST.get('distance', 10))
        order.calculate_total()
        order.payment_method = 'cod'
        order.complete = True
        order.status = 'processing'
        order.payment_status = 'pending'
        order.save()

        # 自动发出下单消息（作为本人发送）
        OrderMessage.objects.create(
            order=order,
            sender=request.user,
            message=f"Hi, I've placed Order #{order.id} totaling ${order.total_price:.2f}. Please confirm the payment."
        )

        messages.success(request, "Order placed successfully. Redirecting to support chat.")
        return redirect('order_chat', order_id=order.id)

    # GET 请求渲染 checkout 页面
    order.calculate_total()
    context = {
        'customer': customer,
        'order': order,
        'order_total': order.total_price,
    }
    return render(request, 'checkout.html', context)

def payment_success(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id, complete=False)
    order.complete = True
    order.status = 'processing'
    order.payment_status = 'completed'
    order.save()
    messages.success(request, "Payment successful! Order placed.")
    return redirect('profile')


def payment_callback(request):
    # Placeholder for future gateways; redirect to checkout for now
    messages.info(request, "No payment processed.")
    return redirect('checkout')


@login_required
def profile(request):
    customer = get_object_or_404(Customer, user=request.user)
    context = {
        'customer': customer,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    customer = get_object_or_404(Customer, user=request.user)
    if request.method == 'POST':
        customer.phone = request.POST['phone']
        customer.address = request.POST['address']
        customer.name = request.POST['name']
        customer.bank_account = request.POST.get('bank_account', '')
        customer.bank_name = request.POST.get('bank_name', '')
        customer.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    context = {
        'customer': customer,
    }
    return render(request, 'edit_profile.html', context)


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query) | Q(
            brand__name__icontains=query)
    )
    context = {
        'products': products,
        'title': f'Search Results for "{query}"',
    }
    return render(request, 'product_list.html', context)


def sale(request):
    products = Product.objects.filter(discount_price__isnull=False)
    context = {
        'products': products,
        'title': 'Sale',
    }
    return render(request, 'product_list.html', context)


def new_in(request):
    products = Product.objects.order_by('-id')[:20]
    context = {
        'products': products,
        'title': 'New In',
    }
    return render(request, 'product_list.html', context)


def brands(request):
    brands = Brand.objects.all()
    context = {
        'brands': brands,
    }
    return render(request, 'brands.html', context)


@login_required
def wishlist(request):
    customer = get_object_or_404(Customer, user=request.user)
    wishlist_items = Wishlist.objects.filter(customer=customer)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist.html', context)


@login_required
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    customer = get_object_or_404(Customer, user=request.user)
    wishlist_item, created = Wishlist.objects.get_or_create(
        customer=customer, product=product)
    if created:
        messages.success(request, f"{product.title} added to your wishlist!")
    else:
        messages.info(request, f"{product.title} is already in your wishlist.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


from .models import OrderMessage

@login_required
def order_chat(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # 权限验证：只能自己或管理员查看
    if request.user != order.customer.user and not request.user.is_staff:
        messages.error(request, "您无权访问此订单对话。")
        return redirect('profile')

    # 处理用户提交新消息
    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            OrderMessage.objects.create(order=order, sender=request.user, message=text)
            return redirect('order_chat', order_id=order_id)

    # 获取所有消息并标记系统消息
    messages_list = order.messages.all()
    for msg in messages_list:
        content = msg.message.lower()
        # 支持两种引号形式 & 多语言起始短语
        if content.startswith("hello, i’ve placed order") or content.startswith("hello, i've placed order") or content.startswith("订单已提交"):
            msg.is_system = True
        else:
            msg.is_system = False

    context = {
        'order': order,
        'messages': messages_list,
    }
    return render(request, 'order_chat.html', context)


urlpatterns = [
    
    path('', views.home, name='home'),
    
]

urlpatterns += i18n_patterns(
    path('set-language/', set_language, name='set_language'),
    # other language-related patterns
)