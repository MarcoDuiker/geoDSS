# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
try:
    import exceptions
except:
    pass

class processor(object):
    '''
    This is a base class meant to sub class.

    Definition
    ----------

    Each processor derived from this class should accept a definition where definition is expected to be a dict having at least:

    'title' (string):                     a human readable title
    'description' (string):               a human readable description (may be empty)

    The definition is coming from a rule as defined in a rule_set.

    Rule example
    ------------

    a useful yaml snippet for defining this minimum:

        rules:
            my_rule_name:
                type: processors.processor_derived_from_this_abstract_class
                title: Any title I like
                description: Anything as long as it is not empty. If you dont wan't a descrition use ""
    '''

    __metaclass__ = ABCMeta

    def __init__(self, name, definition, logger, rules, settings = None):
        self.name = name
        self.definition = definition
        self.result = []
        self.executed = False
        self.logger = logger
        self.rules = rules                                              # this is an object with references to executed rules eg. self.rules.rule_1
        if not 'break_on_error' in self.definition:
            self.definition['break_on_error'] = False
        
        # todo: merge smarter: only set values when in settings so that definition overrules settings
        if settings:
            for key, value in settings.items():
                self.definition[key] = value

    def _finish_execution(self, subject, message = None, log = False, report = False):
        '''
        Convenience function for processors.

        Reports the message to the loggers and the reporters.
        Returns the subject or False depending on `definition['break_on_error']` and the `self.executed` state

        Parameters
        ----------

        `subject` (dict):        the subject
            
        Optional parameters
        -------------------

        `message` (string):        the message to report and/ or log

        `log` (bool):              { True | False } sends the message to the log. Defaults to False.

        `report` (bool):           { True | False } sends the message to the report. Defaults to False.
        '''

        if log and message:
            self.logger.error(message)
        if report and message:
            self.result.append(message)

        if self.definition['break_on_error'] and not self.executed:
            return False
        else:
            return subject


    def _handle_execution_exception(self, subject, message = None, log = True, report = True):
        '''
        Convenience function for processors.

        Reports the message to the loggers and the reporters.
        Returns the subject or False depending on `definition['break_on_error']` and the `self.executed` state.

        Parameters
        ----------
            
        `subject` (dict):        the subject
            
        Optional parameters
        -------------------

        `message` (string):        the message to report and/ or log

        `log` (bool):              { True | False } sends the message to the log. Defaults to True.

        `report` (bool):           { True | False } sends the message to the report. Defaults to True.
        '''

        self._finish_execution(subject, message, log, report)

    @abstractmethod
    def execute():
        '''
        This method should be provided by each test.

        each test should implement a execute method which:

        accepts
        -------

        `subject` (dict):   a dict with test subject properties
            
        sets
        ----

        `self.executed`     to True when succesfully executed

        `self.decision`     to True | False 

        `self.result`       to an interable with strings to appear in the report
            
        Returns
        -------

        A modified subject to continue execution of the rules with the returned subject.

        False to end the execution of the rules.
        '''

        pass
