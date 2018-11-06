# -*- coding: utf-8 -*-


import codecs
import datetime
import json
import locale
import math
import re
import string
import tokenize
import threading
import yaml

try:
    # python2
    from urllib import urlencode
except ImportError:
    # python3
    from urllib.parse import urlencode

try:
    from gdal import ogr, gdal
    gdal.UseExceptions()
except ImportError:
    pass

from contextlib import contextmanager

try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class alter_key(processor):
    '''
    This processor alters a subject key by executing a python expression.
    
    Result
    ------
    
    Keys in the subject on changed by success:
    
    The key which is added/ changed is determined by the definition in the rule set (`result_key`).
    

    Definition
    ----------

    `definition` is expected to be a dict having:

     `result_key` (string):             The name of the key to store the result.
                                        If the key exists, the existing value will be overwritten.
                                        Otherwise a new key will be added.
     
     `expression` (string):             The python expression to execute. 
                                        If expression is a key in the subject then the expression will be 
                                        taken from that key in the subject.
                                        
                                        In the expression refer to a subjects key by: `subject['key_goes_here']`.
                                        In the expression refer to a rule defintion key by `rule['key_goes_here']`.
                                        The following modules are available to the expression:
                                        
                                        - codecs
                                        - datetime
                                        - json
                                        - locale
                                        - math
                                        - ogr (if you have this installed)
                                        - os
                                        - re
                                        - string
                                        - tokenize
                                        - urlencode
                                        - yaml
                                        
     `locale` (string):                 (optional) A temporary locale to use for the expression. eg. `nl_NL.utf-8`
     
     `report_template` (string):        (optional) String (with markdown support) to be reported on success.

                                        The following placeholders will be replaced:
    
     - `{result}`                       The resulting value from the proces.


    Rule example
    ------------

    a suitable yaml snippet would be:

        rules:
        - example:
            type: processors.alter_key
            title: Alter a key
            description: ""
            result_key: url
            expression: subject['url'].replace(' ','%20')
            report_template: "Generated a new key: {result}"

    
    Subject example
    ---------------

    Any subject will do, so this one as well:

        subject = '{"url": "a stupid url with spaces.com"}'
    '''
    
    LOCALE_LOCK = threading.Lock()
    
    @contextmanager
    def _setlocale(self, name):
        '''
        Private method to set a temporary locale.
        '''
        with self.LOCALE_LOCK:
            saved = locale.setlocale(locale.LC_ALL)
            try:
                yield locale.setlocale(locale.LC_ALL, name)
            finally:
                locale.setlocale(locale.LC_ALL, saved)


    def execute(self, subject):
        '''
        Executes the processor.

        `subject` can be any dict.
        
        Result
        ------
        
        Keys changed or added to the subject on success.
        '''

        expression = self.definition["expression"]
        if expression in subject:
            expression = subject[expression]

        rule = self.definition
        try:
            if 'locale' in self.definition:
                with self._setlocale(self.definition['locale']):
                    result = eval( expression )
            else:
                    result = eval( expression )
            subject[self.definition['result_key']] = result
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not execute expression with error: `%s`" % str(error))

        self.executed = True
        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('{result}', str(result))
            self.result.append(result)

        return self._finish_execution(subject)
