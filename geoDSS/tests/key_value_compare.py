# -*- coding: utf-8 -*-

from ..tests.test import test

class key_value_compare(test):
    '''
    this test compares a key from the subject with a value given in the rule definition using an operator given in the rule definition

    definition is expected to be a dict having at least:
        key (string):                       The name of the key in the subject
        value (string|number):              The value to compare with
        operator (string):                  The operator used in the comparison. Supported are
                                                '==', '>', '<', '<=', '>='
        report_template (format string):    Python format string with markdown support to be reported when test is True

    a useful yaml snippet for this test would be:
        rules:
            brzo_true:
                type: tests.key_value_compare
                title: BRZO bedrijf
                description: ''
                key: 'brzo'
                value: 'true',
                operator: '==',
                report_template: "Doorsturen naar"

    a useful subject for this would contain:
        subject = {"brzo": "true"}
    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        subject is expected a dict having:
            <a key> (string):                  the key to test against (the test will not return true when the key is undefined)
        '''

        self.decision = False
        self.result = []
        self.executed = False

        if self.definition['key'] in subject:
            subject_value = subject[self.definition['key']]
            if self.definition['operator'] == '==':
                if subject_value == self.definition['value']:
                    self.decision = True
            elif self.definition['operator'] == '>=':
                if subject_value >= self.definition['value']:
                    self.decision = True
            elif self.definition['operator'] == '<=':
                if subject_value <= self.definition['value']:
                    self.decision = True
            elif self.definition['operator'] == '>':
                if subject_value > self.definition['value']:
                    self.decision = True
            elif self.definition['operator'] == '<':
                if subject_value < self.definition['value']:
                    self.decision = True

        if self.decision:
            self.result.append(self.definition["report_template"])
            self.executed = True

        return          # nothing as this is a test


