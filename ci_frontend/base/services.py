# This file will define the utlity functions for base app
import requests
import pandas as pd
from retrying import retry
from requests import HTTPError, Timeout, ConnectionError, URLRequired
import logging
logger = logging.getLogger(__name__)


CI_BACKEND_REST_API_END_POINT = 'http://127.0.0.1:5000/security/'


class DivGenerator:
    """
    Will act as data retriver and processor, this will query the backend to get
    data from REST API server and then create a pandas data frame for data analysis
    """

    def __init__(self,
                 form_type: str,
                 security_name: str):
        self.form_type: str = form_type
        self.security_name: str = security_name
        self.packet: dict = dict()
        self.data_frame: 'DataFrame Pandas' = None

    @staticmethod
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
        # TODO: Add JSON validation to make sure it's not string or None object
        #       make a static method for validation

    def _convert_data_to_data_frame(self) -> 'Pandas data frame':
        """
        This will take the Raw JSON data(dict form) and convert it into a pandas data frame, it will
        one data frame generated from the JSON data for a single security type
        :return: data_frame
        :rtype: Pndas data frame
        """
        # TODO: add exception handling here with logging
        self.data_frame = pd.DataFrame.from_dict(self.packet,
                                                 orient='index')

    def get_data_generate_data_frame(self,
                                     form_type: str,
                                     security_name: str):
        # TODO: Add exception handling for both the calls
        self._get_data_from_backend_service(form_type,
                                            security_name)
        self._convert_data_to_data_frame()

    #def create_div_from_financial_paramter(self):