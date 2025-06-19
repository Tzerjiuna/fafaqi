from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
class Category(models.Model):
    name = models.CharField(_('分类名称'), max_length=100)
    slug = models.SlugField(_('URL别名'), unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('分类')
        verbose_name_plural = _('分类')

class Brand(models.Model):
    name = models.CharField(
        _('品牌名称'),
        max_length=100
    )
    slug = models.SlugField(
        _('URL别名'),
        unique=True,
        blank=True
    )
    logo = models.ImageField(
        _('品牌LOGO'),
        upload_to='brands/'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('品牌')
        verbose_name_plural = _('品牌')

class Product(models.Model):
    title = models.CharField(_('商品名称'), max_length=255)
    slug = models.SlugField(_('URL别名'), unique=True, blank=True)
    description = models.TextField(_('商品描述'))
    brand = models.ForeignKey(
        Brand, 
        verbose_name=_('品牌'), 
        on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        Category, 
        verbose_name=_('分类')
    )
    price = models.DecimalField(_('原价'), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        _('折扣价'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    image = models.ImageField(_('主图'), upload_to='products/')
    in_stock = models.BooleanField(_('有库存'), default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price


    class Meta:
        verbose_name = _('商品')
        verbose_name_plural = _('商品')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        verbose_name=_('商品'), 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(
        _('商品图片'), 
        upload_to='products/gallery/'
    )

    def __str__(self):
        return f"{self.product.title} 的图片"

    class Meta:
        verbose_name = _('商品图片')
        verbose_name_plural = _('商品图片')

class Customer(models.Model):
    user = models.OneToOneField(
        User, 
        verbose_name=_('用户'), 
        on_delete=models.CASCADE
    )
    phone = models.CharField(
        _('手机号'), 
        max_length=20
    )
    address = models.TextField(
        _('地址')
    )
    name = models.TextField(
        _('姓名')
    )
    bank_account = models.CharField(
        _('银行账号'), 
        max_length=100, 
        null=True, 
        blank=True
    )
    bank_name = models.CharField(
        _('银行名称'), 
        max_length=100, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _('客户')
        verbose_name_plural = _('客户')

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('待处理')),
        ('processing', _('处理中')),
        ('shipped', _('已发货')),
        ('delivered', _('已送达')),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cod', _('货到付款')),
        ('online', _('在线支付')),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', _('待支付')),
        ('completed', _('已支付')),
        ('failed', _('支付失败')),
    )

    customer = models.ForeignKey(
        Customer, 
        verbose_name=_('客户'), 
        on_delete=models.CASCADE
    )
    complete = models.BooleanField(
        _('订单已完成'), 
        default=False
    )
    total_price = models.DecimalField(
        _('总金额'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    status = models.CharField(
        _('订单状态'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    payment_method = models.CharField(
        _('支付方式'), 
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='cod'
    )
    delivery_charge = models.DecimalField(
        _('运费'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    distance_km = models.FloatField(
        _('配送距离（公里）'), 
        default=0.0
    )
    payment_status = models.CharField(
        _('支付状态'), 
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(
        _('创建时间'), 
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('订单')
        verbose_name_plural = _('订单')

    def __str__(self):
        return f"{self.customer.user.username} 的订单 #{self.id}"

    def calculate_delivery_charge(self):
        if self.payment_method == 'cod':
            base_charge = Decimal('5.00')
            per_km_charge = Decimal('1.00')
            self.delivery_charge = base_charge + (Decimal(str(self.distance_km)) * per_km_charge)
        else:
            self.delivery_charge = Decimal('0.00')
        self.save()

    def calculate_total(self):
        items_total = sum(item.get_total() for item in self.orderitem_set.all())
        self.calculate_delivery_charge()
        self.total_price = items_total + self.delivery_charge
        self.save()




class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order', 
        verbose_name=_('订单'), 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'Product', 
        verbose_name=_('商品'), 
        on_delete=models.SET_NULL, 
        null=True
    )
    quantity = models.PositiveIntegerField(
        _('数量'), 
        default=1
    )
    price_at_time = models.DecimalField(
        _('下单时价格'), 
        max_digits=10, 
        decimal_places=2
    )  # Price when added to cart

    def save(self, *args, **kwargs):
        if not self.price_at_time:
            self.price_at_time = self.product.current_price
        super().save(*args, **kwargs)

    def get_total(self):
        if self.price_at_time is None or self.quantity is None:
            return 0
        return self.quantity * self.price_at_time

class Wishlist(models.Model):
    customer = models.ForeignKey(
        Customer, 
        verbose_name=_('客户'), 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, 
        verbose_name=_('商品'), 
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(
        _('加入时间'), 
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('收藏')
        verbose_name_plural = _('收藏')
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.user.username} - {self.product.title}"


class OrderMessage(models.Model):
    order = models.ForeignKey(
        Order, 
        verbose_name=_('订单'), 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        User, 
        verbose_name=_('发送人'), 
        on_delete=models.CASCADE
    )
    message = models.TextField(_('消息内容'))
    timestamp = models.DateTimeField(_('发送时间'), auto_now_add=True)

    class Meta:
        
        ordering = ['timestamp']
        verbose_name = _('订单留言')
        verbose_name_plural = _('订单留言')

    def __str__(self):
        return f"{self.sender.username} 的留言"
