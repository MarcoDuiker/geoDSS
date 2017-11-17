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

        self.result = []
        self.result.append(self.definition["report_template"])
        self.decision = True
        self.executed = True

        return True                    # Returning False will end execution
