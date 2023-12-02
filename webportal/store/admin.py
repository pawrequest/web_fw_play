from django.contrib import admin

from store import models


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.PriceTier)
class PriceTierAdmin(admin.ModelAdmin):
    ...
