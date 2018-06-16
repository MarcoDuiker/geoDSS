# -*- coding: utf-8 -*-

try:
    import exceptions
except:
    pass

from ..tests.test import test

class evaluate(test):
    '''
    This test does a boolean evaluation on two or more already executed rules.
    This is usefull for combining tests.

    It might be useful to add `report: False` to the definition of the rules being evaluated to suppress reporting of those rules. 

    Definition
    ----------

    `definition` is expected to be a dict having at least:

    `expression` (string):                The expression to evaluate.
                                          eg. `"rules.first_test and rules.second_test"`.
                                          Between the named tests python boolan logic and operators can be used like `and`, `or`, `not`.

    `report_template` (string):           String to be reported when the test evaluates to True. May be omited, to only report the reports
                                          from the list given in `add_to_report`.

    `add_to_report` (list):               A list of all named test of which the reports should be added to the report of this test when
                                          the test is True.


    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
        - evaluate_tests_1:
            type: tests.evaluate
            title: evaluating 'and'
            description: test the evaluate test by doing an "unit_test_1 and unit_test_2"
            expression: "rules.unit_test_1 and rules.unit_test_2"
            report_template: unit_test_1 and unit_test_2 is true


    Subject Example
    ---------------

    a useful subject for this would be (any other subject will do as well):

        subject = {'result': True}
    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        `subject`    Is expected to be a dict.
                     (contents doesn't matter)
        '''

        self.logger.debug('Evaluating: %s' % self.definition["expression"]) 

        try:
            rules = self.rules
            self.decision = eval( self.definition["expression"] )
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not succesfully evaluate expression: '%s' with error: %s " % ( self.definition["expression"], str(error)))

        if self.decision:
            if "report_template" in self.definition:
                self.result.append(self.definition["report_template"])
            if 'add_to_report' in self.definition:
                for test_name in self.definition['add_to_report']:
                    self.result.extend(getattr(getattr(rules,test_name), 'result'))
        
        self.executed = True

        return self._finish_execution(subject)
