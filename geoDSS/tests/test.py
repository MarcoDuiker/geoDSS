# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import exceptions

class test(object):
    '''
    Class meant to sub class

    each test should have a definition where definition is expected to be a dict having:
        title (string):                     a human readable title
        description (string):               a human readable description

        when not provided the title will be set from the name; the description will be an empty string.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, name, definition, logger, settings = None):
        self.name = name
        self.definition = definition
        self.decision = False
        self.result = []
        self.executed = False
        self.logger = logger

        # todo: merge smarter: only set values when in settings so that definition overrules settings
        if settings:
            for key, value in settings.items():
                self.definition[key] = value

    def  __bool__(self):
        '''
        provides the decision after executing the test.
        '''

        if self.executed:
            return bool(self.decision)
        else:
            raise exceptions.AttributeError("Test should be executed before evaluation")


    @abstractmethod
    def execute():
        '''
        This method should be provided by each test

        each test should implement a execute method which:
            accepts:
            - subject: a dict with test subject properties
            sets:
            - self.executed = True when succesfully executed
            - self.decision = True | False 
            - self.result to an interable with strings to appear in the report
            should not return a result
        '''
        pass
