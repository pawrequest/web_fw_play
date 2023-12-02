from . import models

#
# class CustomerWidget(s2forms.ModelSelect2Widget):
#     model = models.Customer
#     search_fields = [
#         "name__icontains",
#     ]
#
#
# class ProductWidget(s2forms.ModelSelect2MultipleWidget):
#     search_fields = [
#         "name__icontains",
#     ]

#
# class ItemForm(forms.ModelForm):
#     class Meta:
#         model = Basket
#         exclude = ()
# class NewTransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = "__all__"
#         widgets = {
#             "customer": CustomerWidget,
#         }
