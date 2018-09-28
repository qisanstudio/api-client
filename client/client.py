# -*- coding: utf-8 -*-

import requests
import unittest
from celery import Celery
from logformat import get_color_console_logger


app = Celery('client', broker='redis://localhost:6379')
logger = get_color_console_logger('client')


@app.task
def _request(method, url, **kw):
    """
    COPY FROM https://github.com/requests/requests/blob/master/requests/sessions.py#L461

    copy from requests.session.request
    Constructs a :class:`Request <Request>`, prepares it and sends it.
    Returns :class:`Response <Response>` object.

    :param method: method for the new :class:`Request` object.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query
        string for the :class:`Request`.
    :param is_async: (optional) Either a boolean, use async or not. Defaults to ``False``.
    :param data: (optional) Dictionary, bytes, or file-like object to send
        in the body of the :class:`Request`.
    :param json: (optional) json to send in the body of the
        :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the
        :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the
        :class:`Request`.
    :param files: (optional) Dictionary of ``'filename': file-like-objects``
        for multipart encoding upload.
    :param auth: (optional) Auth tuple or callable to enable
        Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How long to wait for the server to send
        data before giving up, as a float, or a :ref:`(connect timeout,
        read timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Set to True by default.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol or protocol and
        hostname to the URL of the proxy.
    :param stream: (optional) whether to immediately download the response
        content. Defaults to ``False``.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use. Defaults to ``True``.
    :param cert: (optional) if String, path to ssl client cert file (.pem).
        If Tuple, ('cert', 'key') pair.
    :rtype: requests.Response
    """
    session = requests.Session()
    return session.request(method, url, **kw)


class APIClient(object):

    def __init__(self, path=''):
        self._base_url = path

    def __getattr__(self, item):
        name = '{}/{}'.format(self._base_url, item)
        return _Callable(self, name)

    def before_request(self, method, url, kw):
        return method, url, kw

    def request(self, method, url, **kw):
        is_async = kw.pop('is_async', False)
        method, url, kw = self.before_request(method, url, kw)

        if is_async:
            # no response
            return _request.delay(method, url, **kw)
        else:
            return _request(method, url, **kw)


class _Excutable(object):

    def __init__(self, client, method, path):
        self._client = client
        self._method = method.upper()
        if not path.endswith('/'):
            path = path + '/'
        self._path = path

    def __call__(self, **kw):
        return self._client.request(self._method, self._path, **kw)

    def __str__(self):
        return '_Excutable({} {})'.format(self._method, self._path)

    __repr__ = __str__


class _Callable(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, item):
        if item == 'get':
            return _Excutable(self._client, 'GET', self._name)
        elif item == 'post':
            return _Excutable(self._client, 'POST', self._name)
        name = '{}/{}'.format(self._name, item)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' % self._name

    __repr__ = __str__


class TestAPIClient(unittest.TestCase):

    def setUp(self):
        self.client = APIClient('http://localhost:8000')

    def test_urls(self):
        self.assertEqual(self.client.a.b._name, "http://localhost:8000/a/b")


def test_async_request():
    client = APIClient('http://localhost:8000')
    headers = {'Authorization': 'Bearer 2808555096_d09e0cdca8fc4af88e7cc47ed055e6f2'}
    data = {'title': '智勇测试client', 'content': 'xxxxxxx'}
    result = client.wechat_service.help_list.post(headers=headers, data=data, is_async=True)
    logger.debug(result)


if __name__ == '__main__':
    # celery -A client:app worker
    # celery flower -A client:app --broker=redis://localhost:6379/0 --port=5555
    # unittest.main()
    test_async_request()