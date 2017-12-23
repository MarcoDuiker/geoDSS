# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

import traceback

try:
    # python2
    from urllib import urlencode
except ImportError:
    # python3
    from urllib.parse import urlencode

from ..tests.test import test


class request(test):
    '''
    This test fires a request to an URL using the requests module.
    The test can be configured to evaluate to True depending on status codes
    and/ or the response containing a specific string.

    Definition
    ----------

    `definition`     is expected to be a dict having at least:

    `url`            service endpoint for the request

    `verb`           supported html verb. `GET`, `POST` and `HEAD` are supported.

    `params`         a dict with al params for the request. The following optional parameters are supported:
    
    - `basicAuth`       a dict for HTTPBasicAuthentication containing:

       username

       password
       
    - `digestAuth`       a dict for HTTPdigestAuthentication containing:

       username

       password

    - `headers`         A dict containing the headers. eg. `'user-agent': 'my-app/0.0.1'`
    - `verify`          Defaults to `True`. Set to `False` to ignore verifying the SSL certificate.


    `status_codes`   A list of status codes. If the returned status code is NOT in this list, this test evaluates to False.
                     Defaults to `200`.

    `return_value`   When given the test will evaluate to True if the return value is in the response content.
                     If not given, only the returned status code will determine if the test evaluates to True.

    `report_template` (string):     The string to report when the test evaluated to True.
                                    The following placeholders will be replaced:

    - `{text}`                      will be replaced by the text of the response.
    - `{status_code}`               will be replaced by the status code of the response.
    - `{response_time}`             will be replaced with the response time.

    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
            google:
                type: tests.request
                title: See if Google is alive
                description: ""
                url: "https://google.com/search"
                verb: GET
                status_codes:
                - 200
                report_template: "It's alive cause it returned status code {status_code} in {response_time} seconds."

    Subject Example
    ---------------

    a useful subject for this would be:

        subject = {"q": "geoDSS+github"}
    '''

    def execute(self, subject):
        '''
        Executes the test.

        `subject`       is expected a dict which can optionally have:

        - `request_data`   Either a dict or string to POST or GET.
                           In case of a GET or HEAD request, the string will be
                           urlencoded before being appended to the url.
        '''

        params = self.definition
        url = params['url']

        try:
            auth = None
            if 'basicAuth' in params:
                auth = HTTPBasicAuth(**params['basicAuth'])
            if 'digestAuth' in params:
                auth = HTTPDigestAuth(**params['digestAuth'])
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not setup authentication with error: " + str(error))

        verify = True
        if 'verify' in params:
            verify = params['verify']

        headers = None
        if 'headers' in params:
            headers = params['headers']

        status_codes = ['200']
        if 'status_codes' in params:
            status_codes = params['status_codes']

        data = None
        if 'request_data' in subject:
            data = subject['request_data']
        if type(data) == str and not params["verb"] == 'POST':
            # append the string to the url
            if '?' in url:
                if not url[-1] == '&':
                    url = url + '&'
            else:
                url = url + '?'
            url = url + urlencode(data)
            data = None

        if params["verb"] == 'GET':
            try:
                response = requests.get(url, params=data, headers=headers, verify=verify, auth=auth)
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not 'GET' url '%s' with error: %s" % (url, str(error)))
        elif params["verb"] == 'POST':
            try:
                response = requests.post(url, data=data, headers=headers, verify=verify, auth=auth)
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not 'POST' on url '%s' with error: %s" % (url, str(error)))
        elif params["verb"] == 'HEAD':
            try:
                response = requests.head(url, params=data, headers=headers, verify=verify, auth=auth)
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not 'POST' on url '%s' with error: %s" % (url, str(error)))
        else:
            return self._handle_execution_exception(subject, "HTML verb '%s' not supported." % params["verb"])
        
        self.executed = True
        if response.status_code not in params['status_codes']:
            self.decision = False
        else:
            if 'return_value' in params:
                if params['return_value'] in response.text:
                    self.decision = True
                else:
                    self.decision = False
            else:
                self.decision = True

        self.result.append(self.definition["report_template"].replace(
            '{text}', response.text).replace(
            '{status_code}', str(response.status_code)).replace(
            '{response_time}', str(response.elapsed.total_seconds())
        ))

        return self._finish_execution(subject)
