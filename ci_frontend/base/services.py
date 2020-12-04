# This file will define the utlity functions for base app
import requests
import pandas as pd
from retrying import retry
from requests import HTTPError, Timeout, ConnectionError, URLRequired
from plotly.offline import plot
from plotly.graph_objs import Scatter
from plotly import graph_objs as go
import logging

logger = logging.getLogger(__name__)

CI_BACKEND_REST_API_END_POINT = 'http://127.0.0.1:5000/security/'


class DivGenerator:
    """
    Will act as data retriver and processor, this will query the backend to get
    data from REST API server and then create a pandas data frame for data analysis
    e.g
        obj = DivGenerator('10=k',
                            'msft')
    """
    MIN_VALID_YEARS_PER_BACKEND_CALL = 10

    def __init__(self,
                 form_type: str,
                 security_name: str):
        """
        Class will take a form_type which might be something like '10-k', the security name will be a particular
        business entity caller is interested in like 'aapl' for Apple Computers
        :param form_type: SEC form type like e.g '10-k'
        :type form_type: str
        :param security_name: ticker or listing symbol like 'aapl' for Apple Computers
        :type security_name: str
        """
        self.form_type: str = form_type
        self.security_name: str = security_name
        self.packet: dict = dict()
        self.data_frame: 'DataFrame Pandas' = None

    #@staticmethod
    def retry_on_connection_exceptions(exception) -> bool:
        """
        Takes in exception type from function to compare and retry if it meets the exception
        type
        :param exception: requests.Exception
        :type exception: Exception
        :return: True or False
        :rtype: bool
        """
        return isinstance(exception, (Timeout, ConnectionError, HTTPError))

    @retry(retry_on_exception=retry_on_connection_exceptions,
           wait_fixed=1000,
           stop_max_attempt_number=5)
    def _get_data_from_backend_service(self) -> dict:
        """
        This method will pull the data from backend the REST API server and then return
        the value for further processing. Includes error handling and retries for the
        request
        :rtype: dict
        """
        # for eg : 10-k form it will look like http://127.0.0.1:5000/security/10-k/msft/
        final_url = CI_BACKEND_REST_API_END_POINT + self.form_type + '/' + self.security_name + '/'
        # extract the JSON data and send it to the caller
        try:
            self.packet = requests.get(final_url,
                                       timeout=1).json()
        except URLRequired as ue:
            logger.exception("URL %s is not valid err: ",
                             final_url,
                             ue)
        except (Timeout, ConnectionError, HTTPError) as try_again:
            # let retry decorator above take care of this
            logger.exception("Unable to connect ", try_again)
            raise try_again

    def _validate_incoming_data(self):
        """
        A very basic JSON/dict validator for the incoming packet from the backend. In
        case of missing data or no data it will raise a value error stating the packet
        is of no use. Caller needs to handle the exception
        :return: None
        :rtype:
        """
        # Add basic validation for the JSON/dict extracted
        # In case validation becomes large use this package
        # https://github.com/vaidik/incoming
        if self.packet is None or len(self.packet) < self.MIN_VALID_YEARS_PER_BACKEND_CALL:
            raise ValueError

    def _convert_data_to_data_frame(self) -> 'Pandas data frame':
        """
        This will take the Raw JSON data(dict form) and convert it into a pandas data frame, it will
        one data frame generated from the JSON data for a single security type
        :return: data_frame
        :rtype: Pndas data frame
        """
        # data validation is done before this function is called
        self.data_frame = pd.DataFrame.from_dict(self.packet,
                                                 orient='index')

    def get_data_generate_data_frame(self,
                                     form_type: str,
                                     security_name: str):
        """
        Completes the following sequence for each call
        1. Make a call to backend REST API server to get the form based data for a particular security
        2. Perform a basic validation for the incoming data packet
        3. After verification push the packet into a Pandas data frame
        :param form_type: SEC form type like 10-k, 10-q and so on
        :type form_type: str
        :param security_name: Security name like 'aapl' for Apple computer
        :type security_name: str
        :exception :Throws a Value error which needs to be handled by caller
        :return: None
        :rtype: None
        """
        self._get_data_from_backend_service()
        try:
            self._validate_incoming_data()
        except ValueError as ve:
            logger.exception("Incoming packet bad, cannot continue to analyze it :",
                             ve)
            raise ve
        self._convert_data_to_data_frame()

    def create_div_from_financial_paramter(self,
                                           field_name: str) -> 'HTML <div> string':
        """
        Method return a HTML <div> for the field specified. This div string will be retunred to caller to be inserted
        into an HTML template. This div will be created from the data in the pandas data frame matching the column
        name of the field_name.
        e.g - field_name = "accountspayablecurrent"
        :param field_name: This is the field caller wants a graph div for
        :type field_name: str
        :return: HTML <div> string
        :rtype: str
        """
        # check to make sure the field_name exists in the data frame
        if not {field_name}.issubset(self.data_frame.columns):
            raise ValueError
        # reduce CPU load by using logging this way where string is formed if needed
        logger.info("%s %s %s",
                    "Found ",
                    field_name,
                    " generating the <div>")
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.data_frame.index,
                                     y=self.data_frame[field_name],
                                     name=field_name,
                                     opacity=0.8,
                                     line_color='deepskyblue'))
            fig.layout.update(title_text=field_name,
                              xaxis_rangeslider_visible=False)
            plot_div = plot(fig,
                            output_type='div',
                            include_plotlyjs=False)
            # plot_div = plot([Scatter(x=self.data_frame.index,
            #                          y=self.data_frame[field_name],
            #                          mode='lines',
            #                          name=field_name,
            #                          opacity=0.8,
            #                          marker_color='green',
            #                          line_color='deepskyblue')],
            #                 output_type='div',
            #                 include_plotlyjs=False)
        except ValueError as ve:
            logger.exception("Unable to create an HTML <div> for field: %s ",
                             field_name, ve)
            return "oops statstic not found"
        return plot_div
