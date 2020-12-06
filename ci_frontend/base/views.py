from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

# Use class based views to generate a kind of list of parameter graphs, each
# financial parameter is a 1 graph, we will not use any inbuilt DB to retrive
# any data. Only the REST API backend will be used to get the data about
# each security back. This is for form 10-k only as of now
from .models import CommonStock
from .services import DivGenerator


class CommonStockSearchPageView(generic.TemplateView):
    """
    Class controls the display of the search bar page which will be presented to the user
    when they land on the page to search common stock. We have decided to build common stock
    report by used 10-k form which have yearly financial data.
    """
    template_name = 'base/comm-stock-search.html'


class SearchResultsView(generic.ListView):
    """
    This class is the main functionality provider, it will take the inputs from the get call
    in the search bar, the user types company 'ticker symbol' or 'company name' from the S&P
    listed public companies. This class will then make sure the company is listed in the local
    DB for the frontend. Once that is confirmed it will call the analytical information generation
    about that company. It will call the supporting classes like div generator which in turn calls
    the backend REST API server to get company financial data.

    Output:
    The class generates analytical informaiton about the company being queried
    Current added functionality of analytical info generated
    1. Generations of plotly powered graphs to show the financial results about various parameters
    """
    # This is the model that stores the fields for the local frontend DB which contains the list of
    # S&P 500 companies
    model = CommonStock
    context_object_name = 'output'
    template_name = 'base/comm-stock-search-results.html'

    def get_queryset(self) -> 'list[str]':
        """
        This is a custom method which will takes inputs from the search bar using a 'GET' call,
        it will then issue a search query to the fronted DB to make sure the listed company name
        or ticker symbol is valid from the S&P 500 companies. Then based on the ticker symbol and
        form_type it will make calls to helper classes to generate analytical data like graphs to
        present to the user on the search resutls page
        :return: list of Div strings for platly graphs
        :rtype: list
        """
        # gets the HTML form pointer data see HTML file to get context
        query = self.request.GET.get('q')
        object_list = CommonStock.objects.filter(
                        Q(symbol__icontains=query) | Q(Name__icontains=query))
        if object_list.exists():
            # Extract the fields of 'symbol' and 'form_type' as they are needed to build graphs
            extracted_dict = object_list.values('symbol', 'form_type')[0]
            obj = DivGenerator(extracted_dict['form_type'],
                               extracted_dict['symbol'].lower())
            obj.get_data_generate_data_frame(extracted_dict['form_type'],
                                             extracted_dict['symbol'].lower())
            buf = []
            try:
                # logger.debug("Reached the div generator call")
                buf.append(obj.create_div_from_financial_paramter('accountspayablecurrent'))
                buf.append(obj.create_div_from_financial_paramter('accountsreceivablenetcurrent'))
            except ValueError as ve:
                logger.exception("Failed to generate <div> for form:%s BE: %s field:%s ",
                                 extracted_dict['form_type'],
                                 extracted_dict['symbol'].lower(),
                                 'accountspayablecurrent')

            return buf
        else:
            logger.info(f"Not able to locate {query} in the DB")
            return "Opps canot find this company"
