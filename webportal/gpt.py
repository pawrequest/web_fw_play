import decimal
import random
from dataclasses import dataclass

#
#
#
# line_items = [LineItem(random.randrange(1, 10),     # qty
#                   random.randrange(1, 1000),        # id
#                   random.randrange(1, 1000) / 100)  # price
#          for _ in range(10)]

...
from typing import List
#
#
# @dataclass
# class LineItem:
#     quantity: int
#     product_id: int
#
#     @property
#     def name(self):
#         return Product.objects.get(pk=self.product_id).name
#
#     @property
#     def price_each(self):
#         prices = [price_object.price for price_object in PriceTier.objects.filter(product=self.product_id) if
#                   self.quantity >= price_object.min_quantity]
#         return min(prices) if prices else None
#
#     @property
#     def line_total(self):
#         return self.quantity * self.price_each
#
#     def __str__(self):
#         return f'LineItem: {self.quantity} units of {self.name}'
#
#     def __contains__(self, product_id: int):
#         return self.product_id == product_id
#
#
# line_items = [LineItem(random.randrange(1, 10),  # qty
#                        random.randrange(1, 1000))  # id
#               for _ in range(10)]
#
# @dataclass
# class ItemList:
#     line_items: list[LineItem]
#
#     def __contains__(self, product_id: int):
#         return any([line_item.product_id == product_id for line_item in self.line_items])
#
# ILIST = ItemList(line_items=line_items)
# ...


mydict = {
    '1':'1',
}

mydict = int(mydict)
...