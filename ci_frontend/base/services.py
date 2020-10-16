# This file will define the utlity functions for base app
import requests

CI_BACKEND_REST_API_END_POINT = 'http://127.0.0.1:5000/security/'

def get_data_from_rest_api_server(form_type: str,
                                  security_name: str):
    """

    :param form_type: 
    :type form_type: 
    :type security_name: str
    """
    # for eg : 10-k form it will look like http://127.0.0.1:5000/security/10-k/msft/
    final_url = CI_BACKEND_REST_API_END_POINT + form_type + '/' + security_name + '/'
    packet = requests.get(final_url).json()
    #print(packet['2010'])
    return packet
