# -*- coding: utf-8 -*-

import datetime

try:
    import exceptions
except:
    pass

from ..tests.test import test

class remark(test):
    '''
    This test always evaluates to True, regardless of the subject.
    This is usefull for adding comments or remarks to the report.
    
    The keys of the subject can be reported via parameter substitution as well
    as a timestamp.

    Definition
    ----------

    `definition`     is expected to be a dict having at least:

    `report_template` (string):           String  to be reported when the test is True (which is always the case).
                                          The following placeholders will be replaced:

    - `{parameter}`                         where `parameter` is a key in the subject will be replaced by the string representation
                                            of the value.
                                            
    - `{timestamp}`                         will be replaced by the ISO timestamp. 
                                          

    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
            unit_test:
                type: tests.remark
                title: Remember
                description: Remember
                report_template: Remember the milk

    Subject Example
    ---------------

    a useful subject for this would be (and any other subject will do as well):

        subject = {}
    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        `subject`    is expected to be a dict.
                     (contents doesn't matter)
        '''

        result = self.definition["report_template"]                                         # we have the report_template available to manipulate
        for key, value in subject.items():                                                  # in this case we replace place holders by values in the subject
            result = result.replace('{' + key + '}', str(value))
        result = result.replace('{timestamp}', datetime.datetime.now().isoformat())
        
        self.logger.debug('Adding to the report: %s' % result )                             # you have a logger available to log some messages
                                                                                            # the loggers properties are set up in the rule_set definition

        self.decision = True                                                                # don't forget to set self.decision to True,
                                                                                            # otherwise "Test decision is: False" is added to the report instead of the following:

        self.result.append(result)                                                          # in this way we add a string to the report

        self.executed = True                                                                # don't forget to set self.executed to True, 
                                                                                            # otherwise "Error: test is not executed:" will be added to the report as well

        return self._finish_execution(subject)                                              # Returns False to end execution or the subject to continue to the next test 
