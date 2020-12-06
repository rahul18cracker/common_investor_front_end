from django.urls import path

from . import views

urlpatterns = [
    # This is the results page after the search is done
    path('search/',
         views.SearchResultsView.as_view(),
         name='common_stock_search_results'),
    # Landing page with search bar fpr the user
    path('',
         views.CommonStockSearchPageView.as_view(),
         name='common-stock-search')
]
