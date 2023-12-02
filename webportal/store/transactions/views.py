from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from store.models import Product
from core.enums import JScriptKeywords
from .basket import Basket, LineItem


def basket_summary(request):
    basket = Basket(request)
    return render(request, 'store/basket/summary.html', {'basket': basket})


def basket_update(request):
    simple_basket = request.session.get(JScriptKeywords.SESSION_KEY, {})
    basket = Basket.from_string_basket(simple_basket)
    product_id = int(request.POST.get(JScriptKeywords.BASKET_PRODUCT_ID))
    product_qty = int(request.POST.get(JScriptKeywords.BASKET_PRODUCT_QTY))

    action = request.POST.get(JScriptKeywords.BASKET_ACTION)
    if action == JScriptKeywords.BASKET_ACTION_UPDATE:
        basket[product_id] = product_qty
    elif action == JScriptKeywords.BASKET_ACTION_ADD:
        basket[product_id] = basket[product_id].quantity + product_qty
    elif action == JScriptKeywords.BASKET_ACTION_DELETE_ITEM:
        del basket[product_id]

    request.session[JScriptKeywords.SESSION_KEY] = basket.to_str_dict_basket()
    return basket.get_response()
