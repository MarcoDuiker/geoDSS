# -*- coding: utf-8 -*-

import datetime
import traceback
import os

try:
    import requests
    from requests.auth import HTTPBasicAuth
    from requests.auth import HTTPDigestAuth
except:
    pass
    
try:
    # python2
    from urllib import urlencode
except ImportError:
    # python3
    from urllib.parse import urlencode

try:
    import exceptions
except:
    pass

from ..tests.test import test


class request(test):
    '''
    This test fires a request to an URL using the requests module.
    The test can be configured to evaluate to True depending on status codes
    and/ or the response containing a specific string.

    Definition
    ----------

    `definition`     is expected to be a dict having at least:

    `url`            Service endpoint for the request. You may also give a string. 
                     If this string is a key in the subject the url will be taken from subject. 

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
                     If `None` or not given the test will NOT eveluate to False based on the returned status_code.

    `return_value`   When given the test will evaluate to True if the return value is in the response content.
                     If not given, only the returned status code will determine if the test evaluates to True.
                     If `return_value` is a key in the subject, then the value of that key is used.

    `report_template` (string):     The string to report when the test evaluated to True.
                                    The following placeholders will be replaced:

    - `{text}`                      will be replaced by the text of the response.
    - `{status_code}`               will be replaced by the status code of the response.
    - `{response_time}`             will be replaced with the response time.
    - `{timestamp}`                 will be replaced by the ISO timestamp. 

    `return_subject_key`    When given, this subject key will receive the response.

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

        - `request_data`   Either a dict or string to POST or GET. If the string
                           is a path to a file this file is read to get a string.
                           In case of a GET or HEAD request, the string will be
                           urlencoded before being appended to the url.
        '''

        
        url = self.definition['url']
        if url in subject:
            url = subject[url]

        auth = None
        verify = True
        headers = None
        
        if 'params' in self.definition:
            params = self.definition['params']
            try:
                if 'basicAuth' in params:
                    auth = HTTPBasicAuth(**params['basicAuth'])
                if 'digestAuth' in params:
                    auth = HTTPDigestAuth(**params['digestAuth'])
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not setup authentication with error: " + str(error))
            if 'verify' in params:
                verify = params['verify']
            if 'headers' in params:
                headers = params['headers']

        status_codes = None
        if 'status_codes' in self.definition:
            status_codes = self.definition['status_codes']

        data = None
        if 'request_data' in subject:
            data = subject['request_data']
            self.logger.debug("Using %s with type: %s as data" % (str(data), type(data)))
        if isinstance(data, basestring) and os.path.exists(data):
            self.logger.debug("Reading %s as data" % (str(data)))
            with open(data,'rb') as stream:
                data = stream.read()
        if isinstance(data, basestring) and not self.definition["verb"] == 'POST':
            # append the string to the url
            if '?' in url:
                if not url[-1] == '&':
                    url = url + '&'
            else:
                url = url + '?'
            url = url + urlencode(data)
            data = None

        if self.definition["verb"] == 'GET':
            try:
                response = requests.get(url, params=data, headers=headers, verify=verify, auth=auth)
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not 'GET' url '%s' with error: %s" % (url, str(error)))
        elif self.definition["verb"] == 'POST':
            try:
                response = requests.post(url, data=data, headers=headers, verify=verify, auth=auth)
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not 'POST' on url '%s' with error: %s" % (url, str(error)))
        elif self.definition["verb"] == 'HEAD':
            try:
                response = requests.head(url, params=data, headers=headers, verify=verify, auth=auth)
            except Exception as error:
                return self._handle_execution_exception(subject, "Could not 'HEAD' url '%s' with error: %s" % (url, str(error)))
        else:
            return self._handle_execution_exception(subject, "HTML verb '%s' not supported." % self.definition["verb"])
        
        self.executed = True
        if status_codes and response.status_code not in status_codes:
            self.decision = False
        else:
            if 'return_value' in self.definition:
                if self.definition['return_value'] in subject:
                    rv = subject[self.definition['return_value']]
                else:
                    rv = self.definition['return_value']
                if rv in response.text:
                    self.decision = True
                else:
                    self.decision = False
            else:
                self.decision = True

        if self.decision:
            self.result.append(self.definition["report_template"].replace(
                '{text}', response.text).replace(
                '{status_code}', str(response.status_code)).replace(
                '{response_time}', str(response.elapsed.total_seconds())).replace(
                '{timestamp}', datetime.datetime.now().isoformat())
            )

        if 'return_subject_key' in self.definition:
            subject[self.definition['return_subject_key']] = response.text

        return self._finish_execution(subject)
