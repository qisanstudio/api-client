# -*- coding: utf-8 -*-

from client.client import APIClient
from client.client import logger


class ESAPIClient(APIClient):

    def before_request(self, method, url, kw):
        headers = kw.get('headers', {})

        header_key_l = [k.lower() for k in headers.keys()]
        if 'content-type' not in header_key_l:
            headers['content-type'] = "application/json"

        kw['headers'] = headers
        return method, url, kw
