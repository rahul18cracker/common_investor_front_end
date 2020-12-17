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

# ============== CODE BELOW HERE IS EXPERMENTAL AND NEEDS TO BE CLEANED UP ==============
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
    template_name = 'base/ajax-test.html'

    # template_name = 'base/comm-stock-search-results.html'
    def render_to_response(self,
                           context,
                           **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        logging.critical("Entered the render response function")
        query = self.request.GET.get('q')
        object_list = CommonStock.objects.filter(
            Q(symbol__icontains=query) | Q(Name__icontains=query))
        if self.request.is_ajax():
            html = render_to_string(
                template_name="base/ajax-results-partial.html",
                context={"companies": object_list}
            )

            data_dict = {"html_from_view": html}
            logger.debug("in AJAX VIEW: Giving JSON response for AJAX")
            return JsonResponse(data=data_dict,
                                safe=False,
                                **response_kwargs)
        else:
            # Regular HTTP request
            return super(SearchResultsView, self).render_to_response(context, **response_kwargs)


# ============ AJAX Experimental code begins ==========
def ajax_view(request):
    ctx = {}
    url_parameter = request.GET.get("q")
    logger.debug(f"in AJAX VIEW : url_parameter : {url_parameter}")

    if url_parameter:
        logger.debug(f"in AJAX VIEW: Entered URL paramter if to get object list")
        object_list = CommonStock.objects.filter(
            Q(symbol__icontains=url_parameter) | Q(Name__icontains=url_parameter))
        logger.debug(f"Object list is {object_list.values('symbol', 'Name', 'Sector')}")
    else:
        logger.debug(f"in AJAX VIEW: url_parameter not found in else case")
        # object_list = CommonStock.objects.all()
        object_list = []

    ctx["companies"] = object_list
    # AJAX only request return
    logger.debug("in AJAX VIEW: Going for AJAX check")
    if request.is_ajax():
        html = render_to_string(
            template_name="base/ajax-results-partial.html",
            context={"companies": object_list}
        )

        data_dict = {"html_from_view": html}
        logger.debug("in AJAX VIEW: Giving JSON response for AJAX")
        return JsonResponse(data=data_dict, safe=False)
    # HTML request return
    # logger.debug(f"in AJAX VIEW: Sending html response {object_list.values('symbol')[0]}")
    if object_list:
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

        # return buf
        ctx['output'] = buf
    return render(request, "base/ajax-test.html", context=ctx)
    # return render(request, "base/ajax-test.html", context=ctx)

# ============ AJAX Experimental code ends ==========
