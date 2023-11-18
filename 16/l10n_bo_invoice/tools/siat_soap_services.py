# -*- coding: utf-8 -*-
import requests
import logging
from zeep.exceptions import Fault
from zeep import Client, Transport
from requests.exceptions import ConnectionError as ReqConnectionError, HTTPError, ReadTimeout

_logger = logging.getLogger(__name__)


class SiatSoapServices:
    endpoint = False
    token = False
    response = False

    def __init__(self, endpoint, token, params, method):
        self.endpoint = endpoint
        self.token = token
        self.params = params
        self.method = method

    def get_headers(self):
        headers = {
            "apikey": "TokenApi {token}".format(token=self.token)
        }
        session = requests.Session()
        session.headers.update(headers)
        return session

    def process_soap_siat(self):
        try:
            transport = Transport(session=self.get_headers())
            client = Client(wsdl=self.endpoint, transport=transport)
            call_wsdl = getattr(client.service, self.method)
            soap_response = call_wsdl(**self.params)
            response = {'success': True, 'data': soap_response}
        except Fault as fault:
            response = {'success': False, 'error': fault.message}
        except ReqConnectionError as connectionError:
            response = {'success': False, 'error': connectionError}
        except HTTPError as httpError:
            response = {'success': False, 'error': httpError}
        except TypeError as typeError:
            response = {'success': False, 'error': typeError}
        except ReadTimeout as timeOut:
            response = {'success': False, 'error': timeOut}
        return response
