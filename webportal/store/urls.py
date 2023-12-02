from django.urls import include, path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_all, name='product_all'),

    # path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>', views.product_detail, name='product_detail'),

    path('shop/<slug:category_slug>/', views.category_list, name='category_list'),

    path("select2/", include("django_select2.urls")),
    # path('new', views.TransactionNewView.as_view(), name='new_transaction'),
]

# path('products', views.ProductListView.as_view(), name='product_list'),
