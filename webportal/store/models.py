from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SaleProductManager(models.Manager):
    def get_queryset(self):
        return super(SaleProductManager, self).get_queryset().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PriceTier(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='sale_price')
    min_quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='images/', default='images/default.png')
    description = models.CharField(max_length=200, null=True)

    objects = models.Manager()
    products = SaleProductManager()

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def sales_price_tiers(self):
        return PriceTier.objects.filter(product=self.pk)

    @property
    def min_price(self):
        return min(sales_ob.price for sales_ob in PriceTier.objects.filter(product=self))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

