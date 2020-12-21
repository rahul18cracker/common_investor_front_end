from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

# Use class based views to generate a kind of list of parameter graphs, each
# financial parameter is a 1 graph, we will not use any inbuilt DB to retrive
# any data. Only the REST API backend will be used to get the data about
# each security back. This is for form 10-k only as of now
from .models import CommonStock
from .services import DivGenerator


class CommonStockSearchPageView(generic.ListView):
    """
    Class controls the display of the search bar page which will be presented to the user
    when they land on the page to search common stock. We have decided to build common stock
    report by used 10-k form which have yearly financial data. There is a 2 part handling in
    this, first part handles the AJAX request when the user types the company name or the
    ticker symbol in the search box. The second part is a regular http request handling when
    a user presses enter on the company name or the ticker symbol. Once a regular HTTP request
    is made the expectation is to generate analytical reports
    Summary:
    1. User is presented with search bar
    2. User types and resonse is via AJAX to show if ticker symbol exists
    3. User would press enter and analytical report is generated
    """
    # Set the template names and select a data model to use for stock serach
    template_name = 'base/ajax-test.html'
    model = CommonStock
    # HTTP get response object returned back to user
    context_object_name = 'output'

    def render_to_response(self,
                           context,
                           **response_kwargs) -> 'AJAX html/HTTP Response HTML':
        """
        Method has 2 jobs
        1. When user types in search bar return an AJAX response after querying the DB
           to present to a user that the ticker symbol or company name exists
        2. When users presses enter the DB is queried and the analytical report is gnerated
           and returned
        :param context: Context instance to render the template with (NOT USED BELOW)
        :type context: dict
        :param response_kwargs: Keyword args (NOT USED BELOW)
        :type response_kwargs: dict
        :return: AJAX html and HTTP Response
        :rtype: HTML
        """
        ctx = {}
        ctx['output'] = " "
        # ======= AJAX ONLY PART ===========
        if self.request.is_ajax():
            # Avoid any logging here as this is hit too much with per key pressed
            query = self.request.GET.get('q')
            object_list = CommonStock.objects.filter(
                Q(symbol__icontains=query) | Q(Name__icontains=query))
            html = render_to_string(
                template_name="base/ajax-results-partial.html",
                context={"companies": object_list}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict,
                                safe=False,
                                **response_kwargs)
        else:
            # Regular HTTP request
            query = self.request.GET.get('q')
            # Make sure to check query, if the user has not typed any name then
            # template should render the html page with Search bar blank
            if query:
                object_list = CommonStock.objects.filter(
                    Q(symbol__icontains=query) | Q(Name__icontains=query))
                if object_list:
                    extracted_dict = object_list.values('symbol', 'form_type')[0]
                    obj = DivGenerator(extracted_dict['form_type'],
                                       extracted_dict['symbol'].lower())
                    obj.get_data_generate_data_frame(extracted_dict['form_type'],
                                                     extracted_dict['symbol'].lower())
                    buf = []
                    try:
                        buf.append(obj.create_div_from_financial_paramter('accountspayablecurrent'))
                        buf.append(obj.create_div_from_financial_paramter('accountsreceivablenetcurrent'))
                    except ValueError as ve:
                        logger.exception("Failed to generate <div> for form:%s BE: %s field:%s ",
                                         extracted_dict['form_type'],
                                         extracted_dict['symbol'].lower(),
                                         'accountspayablecurrent')

                    ctx['output'] = buf
                    ctx['companies'] = object_list
                    logger.debug(f"returning the analytical report for {extracted_dict['symbol'].lower()}")
            return render(self.request,
                          "base/ajax-test.html", context=ctx)
