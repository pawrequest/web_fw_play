from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import ListView

from core.enums import JScriptKeywords
from store.models import Category, Product


# Create your views here.
def home(request):
    return render(request, 'home.html')


class ProductListView(ListView):
    model = Product
    template_name = 'store/product-list.html'
    context_object_name = 'products'
    ordering = ['name']


class ProductDetailView(View):
    model = Product
    template_name = 'product-detail.html'
    context_object_name = 'product'

#
# class TransactionNewView(CreateView):
#     template_name = 'store/new-transaction.html'
#     model = Transaction
#     form_class = NewTransactionForm
#     success_url = "/"
#

def product_all(request):
    products = Product.products.all()
    return render(request, 'home.html', {'products': products})


def category_list(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'store/products/category.html', {'category': category, 'products': products})

#
# def product_detail(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     return render(request, 'store/products/single.html', {'product': product})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    context = {
        'jscriptkeywords': JScriptKeywords,
        'product': product,
    }
    return render(request, 'store/products/single.html', context)
