from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    in_stock = models.BooleanField(default=True)

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20, choices=[('cod', 'Cash on Delivery'), ('online', 'Online Payment')], default='cod')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    distance_km = models.FloatField(default=0.0)
    payment_status = models.CharField(max_length=20,
                                      default='pending', 
                                      choices=[('pending', 'Pending'),
                                               ('completed', 'Completed'),
                                               ('failed', 'Failed')])
    def calculate_delivery_charge(self):
        if self.payment_method == 'cod':
            base_charge = 5.00  # Base fee in $
            per_km_charge = 1.00  # $1 per km
            self.delivery_charge = base_charge + (self.distance_km * per_km_charge)
        else:
            self.delivery_charge = 0.00  # Free shipping for online payment
        self.save()

    def calculate_total(self):
        items_total = sum(item.get_total() for item in self.orderitem_set.all())
        self.calculate_delivery_charge()  # Update delivery charge before total
        self.total_price = items_total + self.delivery_charge
        self.save()

    def __str__(self):
        return f"Order #{self.id} by {self.customer.user.username}"

    def calculate_total(self):
        total = sum(item.get_total() for item in self.orderitem_set.all())
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price when added to cart

    def save(self, *args, **kwargs):
        if not self.price_at_time:
            self.price_at_time = self.product.current_price
        super().save(*args, **kwargs)

    def get_total(self):
        return self.quantity * self.price_at_time

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.user.username} - {self.product.title}"