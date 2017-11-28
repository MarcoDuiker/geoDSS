# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
try:
    import exceptions
except:
    pass

class processor(object):
    '''
    Class meant to sub class

    each processor should have a definition where definition is expected to be a dict having:
        title (string):                     a human readable title
        description (string):               a human readable description

        when not provided the title will be set from the name; the description will be an empty string.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, name, definition, logger, settings = None):
        self.name = name
        self.definition = definition
        self.result = []
        self.executed = False
        self.logger = logger
        if not 'break_on_error' in self.definition:
            self.definition['break_on_error'] = False
        
        # todo: merge smarter: only set values when in settings so that definition overrules settings
        if settings:
            for key, value in settings.items():
                self.definition[key] = value

    def _finish_execution(self, subject, message = None, log = False, report = False):
        '''
        Convenience function for processors

        Reports the message to the loggers and the reporters.
        Returns the subject or False depending on definition['break_on_error'] and the self.executed state

        parameters:
            subject:        the subject
            
        optional parameters
            message:        the message to report and/ or log
            log:            { True | False } sends the message to the log. Defaults to False
            report:         { True | False } sends the message to the report. Defaults to False
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
        Convenience function for processors

        Reports the message to the loggers and the reporters.
        Returns the subject or False depending on definition['break_on_error'] and the self.executed state

        parameters:
            subject:        the subject
            
        optional parameters
            message:        the message to report and/ or log
            log:            { True | False } sends the message to the log. Defaults to True
            report:         { True | False } sends the message to the report. Defaults to True
        '''

        self._finish_execution(subject, message, log, report)

    @abstractmethod
    def execute():
        '''
        This method should be provided by each processor

        each processor should implement a execute method which:
            accepts:
            - subject: a dict with test subject properties
            returns:
            - subject: a modified dict with test subject properties
            - if False is returned as a subject the execution of the rules will be ended.
        '''
        pass
