from store.models import Product


def categories(request):
    return {
        'categories': Product.objects.all()
    }
