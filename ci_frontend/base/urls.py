from django.urls import path

from . import views

urlpatterns = [
    # Landing page with search bar for the user
    path('',
         views.CommonStockSearchPageView.as_view(),
         name='companies'),
]
