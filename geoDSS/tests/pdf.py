# -*- coding: utf-8 -*-

import datetime
import glob
import traceback
import os
import subprocess
import tempfile

import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
   
try:
    # python2
    from urllib import urlencode
except ImportError:
    # python3
    from urllib.parse import urlencode

# test if pdfbox is available
found = False
jars = glob.glob(os.path.abspath(os.path.join(os.path.dirname(__file__),
    '../libs/pdfbox/*.jar')))
for jar in jars:
    if 'pdfbox-app' in jar:
        found = True
        pdfbox = os.path.abspath(jar)
if not found:
    raise Exception()

try:
    from fuzzywuzzy import fuzz 
    from fuzzywuzzy import process 
except:
    # we won't be able to do fuzzy matching
    pass

try:
    import exceptions
except:
    pass

from ..tests.test import test


class pdf(test):
    '''
    This test fires a request to an URL using the requests module and extracts
    all text.
    The test can be configured to evaluate to True depending on status codes
    and/ or the text containing a specific string.
    
    Dependencies
    ------------
    
    - pdfbox and a JAVA Runtime     (drop a pdfbox-app-*.jar in the geoDSS libs folder)
    - fuzzywuzzy                    (optional, but fuzzy matching won't be possible without this module)

    Definition
    ----------

    `definition`     is expected to be a dict having:

    `url`            Service endpoint for the request. You may also give a string. 
                     If this string is a key in the subject the url will be taken from subject. 
                     
                     The url may contain placeholders which will be replaced with values from the 
                     given keys in the subject. A placeholder is written like `{subject_key_goes_here}`.

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

    `report_template` (string):     The string to report when the test evaluated to True.
                                    The following placeholders will be replaced:

    - `{status_code}`               will be replaced by the status code of the response.
    - `{response_time}`             will be replaced with the response time.
    - `{timestamp}`                 will be replaced by the ISO timestamp. 
    - `{url}`                       will be replaced by the url of the pdf.
    - `{score}`                     will be replaced by the fuzzy matching score, 
                                    or 100 when no fuzzy matching is done.     
        
    `return_subject_key`            When given, this subject key will receive the response.

    optionally having one of:

    `status_codes`   A list of status codes. If the returned status code is NOT in this list, this test evaluates to False.
                     If `None` or not given the test will NOT eveluate to False based on the returned status_code.

    optionally having:
    
    `search_string`         If this string is a key in the subject the search_string will be taken from subject. 
                            Defaults to `search_string`.
    
    `fuzzy_score`           When given fuzzy matching of the `search_string` is done. 

    Rule example
    ------------

    a useful yaml snippet for this test would be:

        name: pdf
        title: Found in pdf
        description: ""
        logging:
          level: DEBUG
        rules:
        - reddit_gis_search
            type: tests.rss
            title: Found in RSS feed
            description: ""
            url: "https://www.reddit.com/r/gis/.rss"
            verb: GET
            status_codes:
            - 200
            rss_item: content
            fuzzy_score: 10
            limit: 3
            report_template: "{score}: <{link}>"

    Subject Example
    ---------------

    a useful subject for this would be:

        subject = {"search_string":"data science"}
    '''

    def execute(self, subject):
        '''
        Executes the test.

        `subject`       is expected a dict which can optionally have:

        - `request_data`   Either a dict or string to POST or GET. If the string
                           is an absolute or relative path to a file this file is 
                           read to get a string.
                           In case of a GET or HEAD request, the string will be
                           urlencoded before being appended to the url.
                           
        - `search_string`  Search the text extracted from the pdf defined in the rule set for this string.   
        '''
        
        search_string_key = 'search_string'
        if 'search_string' in self.definition:
            search_string_key = self.definition['search_string']
        search_string = None
        if search_string_key in subject:
            search_string = subject[search_string_key]

        url = self.definition['url']
        if url in subject:
            url = subject[url]
        for key in subject.keys():
            if "{%s}" % subject[key] in url:
                url = url.replace("{%s}" % subject[key],subject[key])

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
        if isinstance(data, basestring):
            if os.path.exists(os.path.join(os.getcwd(),data)):
                data = os.path.join(os.getcwd(),data)
            if os.path.exists(data):
                self.logger.debug("Reading %s as data" % (str(data)))
                with open(data,'rb') as stream:
                    data = stream.read()
                    self.logger.debug("Using %s with type: %s as data" % (str(data), type(data)))
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
            if 'search_string' in subject:
                COMMAND = "java -jar {pdfbox} ExtractText -console {fname}"
                fd, fname = tempfile.mkstemp(suffix = '.pdf')
                with os.fdopen(fd, 'wb') as f:
                    f.write(response.content)
                text = subprocess.check_output(COMMAND.format(pdfbox = pdfbox, fname = fname), shell=True).decode('utf-8')
                os.remove(fname)
                text = text.replace('-\n','').replace('\n',' ') 
                if search_string in text:
                    self.decision = True
                    score = 100
                elif 'fuzzy_score' in self.definition:
                    score = fuzz.partial_ratio(search_string, text)
                    if score >= self.definition['fuzzy_score']:
                        self.decision = True
            else:
                self.decision = True

        if self.decision:
            result = self.definition["report_template"].replace(
                '{status_code}', str(response.status_code)).replace(
                '{response_time}', str(response.elapsed.total_seconds())).replace(
                '{timestamp}', datetime.datetime.now().isoformat()).replace(
                '{score}', str(score)).replace(
                '{url}', url) 
            self.result.append(result)

        if 'return_subject_key' in self.definition:
            subject[self.definition['return_subject_key']] = text

        return self._finish_execution(subject)
