# -*- coding: utf-8 -*-

from ..tests.test import test

class remark(test):
    '''
    this test is always true, regardless of the subject.
    this is usefull for adding comments or remarks to the report 

    definition is expected to be a dict having at least:
        report_template (format string):    Python format string with markdown support to be reported

    a useful yaml snippet for this test would be:
            rules:
                unit_test:
                    type: tests.remark
                    title: Remember
                    description: Remember
                    report_template: Remember the milk

    a useful subject for this would be (and any other subject will do as well):
        subject = {}
    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        subject is expected a dict (contents doesn't matter)
        '''

        self.decision = True                                            # don't forget to set self.decision to True,
                                                                        # otherwise "Test decision is: False" is added to the report instead of the following:

        self.result.append(self.definition["report_template"])          # in this way we add the report_template to the report
        
        self.executed = True                                            # don't forget to set self.executed to True, 
                                                                        # otherwise "Error: test is not executed:" will be added to the report as well

        return subject                                                  # Return the subject to continue to the next test or processor. Returning False will end execution
