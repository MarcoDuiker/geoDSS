# -*- coding: utf-8 -*-

from ..tests.test import test

class unit_test(test):
    '''
    this test provides a unit test

    definition is expected to be a dict having at least:
        report_template (format string):    Python format string with markdown support to be reported when test is True

    a useful yaml snippet for this test would be:
            rules:
                unit_test:
                    type: tests.unit_test
                    title: unit test
                    description: unit test testing
                    report_template: Action should be taken

    a useful subject for this would be:
        subject = {'result': True}
    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        subject is expected a dict having:
            result (bool):                  the intended result of the test
        '''

        self.logger.debug('Result asked: %s' % subject['result'])

        if subject['result']:
            self.result.append(self.definition["report_template"])
            self.decision = True

        self.executed = True

        if self.definition['break_on_error']:
            return self.executed
        return True                    # Returning False will end execution
