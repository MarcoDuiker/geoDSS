# -*- coding: utf-8 -*-

from ..tests.test import test

class unit_test(test):
    '''
    This test provides sort of a unit test.

    Definition
    ----------

    definition is expected to be a dict having at least:

    `report_template` (string):           String to be reported when the test is True.

   
    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
            test123:
                type: tests.unit_test
                title: unit test
                description: unit test testing
                report_template: Test evaluated to True, so probably some action is reported here

    Subject example
    ---------------

    a useful subject for this would be:

        subject = {'result': True}
    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        `subject` is expected a dict having:

        `result` (bool):                  the intended result of the test
        '''

        self.logger.debug('Result asked: %s' % subject['result'])
        
        if subject['result']:
            self.result.append(self.definition["report_template"])
            self.decision = True
        else:
            self.result.append("Expected key 'result' was not found in subject.")
        self.executed = True

        return self._finish_execution(subject)


