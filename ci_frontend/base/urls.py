from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('cstock/',
         views.CommonStockListView.as_view(),
         name='cstock'),
]
