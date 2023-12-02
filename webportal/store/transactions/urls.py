from django.urls import path

from store.transactions import views

app_name = 'basket'

urlpatterns = [
    path('', views.basket_summary, name='basket_summary'),
    path('update/', views.basket_update, name='basket_update'),
]
