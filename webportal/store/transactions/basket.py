import sys
from collections import namedtuple
from typing import Dict

from django.db import models
import decimal
from dataclasses import dataclass

from django.http import JsonResponse

from core.enums import JScriptKeywords
from store.models import Customer, PriceTier, Product

import logging


def get_my_logger():
    new_logger = logging.getLogger(name=__name__)
    logging.basicConfig(
        level=logging.INFO,
        format='{asctime} - {levelname:<8} - {funcName} in {filename} on line {lineno} : {message}',
        style='{',
        handlers=[
            logging.FileHandler(f'{__file__}.log', mode='a'),
            logging.StreamHandler(sys.stdout)
        ])
    return new_logger


logger = get_my_logger()


## order
@dataclass
class LineItem:
    quantity: int
    product: Product

    @classmethod
    def from_ints(cls, quantity: int, product_id: int):
        return cls(product=Product.objects.get(id=product_id), quantity=quantity)

    @classmethod
    def from_strs(cls, quantity: str, product_id: str):
        return cls(product=Product.objects.get(id=int(product_id)), quantity=int(quantity))

    @property
    def price_each(self):
        prices = [price_object.price for price_object in PriceTier.objects.filter(product_id=self.product.id)
                  if self.quantity >= price_object.min_quantity]
        return min(prices) if prices else None

    def edit_qty(self, qty: int):
        self.quantity = qty

    @property
    def line_total(self):
        line_tot = self.quantity * self.price_each
        return line_tot

    def __str__(self):
        return f'LineItem: {self.quantity} units of {self.product.name}'

    def __repr__(self):
        return self.__str__()


@dataclass
class Basket:
    def __init__(self, line_items: [LineItem]):
        self.line_items = line_items

    def __contains__(self, prod_id: int):
        return prod_id in [item.product.id for item in self.line_items]

    def __getitem__(self, product_id):
        if product_id in self:
            return next(item for item in self.line_items if item.product.id == product_id)
        raise KeyError(f"No LineItem with product_id {product_id} found in Basket")

    def __setitem__(self, product_id: int, qty: int):
        try:
            self[product_id].edit_qty(qty)
        except KeyError:
            self.line_items.append(LineItem.from_ints(quantity=qty, product_id=product_id))

    def __iter__(self):
        return iter(self.to_str_dict_basket())

    def __len__(self):
        return sum([item.quantity for item in self.line_items])

    def __str__(self):
        # rows = [f'{item.quantity} units of {item.product.name}' for item in self.line_items]
        # return f'Basket: with {len(self)} items: {rows}'
        return f'{[item.__str__() for item in self.line_items]}'

    def __repr__(self):
        # return self.to_str_dict_basket()
        return f'Basket of {len(self)} items:{[item.__repr__() for item in self.line_items]}'
    def get_response(self):
        return JsonResponse({JScriptKeywords.BASKET_QTY: self.__len__(), JScriptKeywords.BASKET_SUBTOTAL: self.subtotal})

    @property
    def subtotal(self):
        return sum([item.line_total for item in self.line_items])

    @classmethod
    def from_string_basket(cls, string_basket: dict[str, str]):
        """ string_basket is a dict of product_id: quantity"""
        return cls([LineItem.from_strs(product_id=prod, quantity=quantity)
                    for prod, quantity in string_basket.items()])

    def to_str_dict_basket(self) -> dict:
        """ string_basket is a dict of product_id: quantity"""
        return {item.product.id: item.quantity for item in self.line_items}

    def delete(self, product_id_to_del: int):
        self.line_items = [item for item in self.line_items if item.product.id != product_id_to_del]


class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=12.00)
    # product_id : quantity
    basket: Basket

    @property
    def subtotal(self):
        return self.basket.subtotal

    @property
    def total(self):
        return self.subtotal + self.shipping_cost

    @property
    def vat(self):
        return self.total * decimal.Decimal(0.2)

    @property
    def grand_total(self):
        return self.total + self.vat

    def __str__(self):
        return f'Transaction: {self.customer.name} on {self.timestamp}'


""" 
Code in this file has been inspried/reworked from other known works. Plese ensure that
the License below is included in any of your work that is directly copied from
this source file.


MIT License

Copyright (c) 2019 Packt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 
"""
