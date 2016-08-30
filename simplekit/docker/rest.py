import httplib
import logging
import time
from json import dumps

import requests
from simplekit import objson

__author__ = 'benjamin.c.yan'

_default_session = requests.Session()

logger = logging.getLogger('stopwatch')


def send_rest(url, method='GET', body=None, timeout=120, session=None, headers=None, proxies=None):
    all_headers = {'Content-Type': 'Application/json'}
    if headers:
        all_headers.update(headers)
    if not session:
        session = _default_session
    session.trust_env = False
    if hasattr(body, "dumps"):
        body = body.dumps()
    elif body and not isinstance(body, basestring):
        body = dumps(body)

    try:
        # retry when response code equal 503 and connection error
        now = time.time()
        response = session.request(method, url,
                                   data=body,
                                   headers=all_headers,
                                   proxies=proxies,
                                   timeout=timeout)
        logger.info('{method} {url} {body} : time elapse {elapse} s'.format(method=method, url=url, body=body,
                                                                            elapse=time.time() - now))
        result = objson.loads(response.content)

        return response.status_code, result
    except (requests.Timeout, requests.ConnectionError), e:
        logger.error('retry because of network error %s %s error: %s' % (method, url, e))

    return httplib.SERVICE_UNAVAILABLE, None
