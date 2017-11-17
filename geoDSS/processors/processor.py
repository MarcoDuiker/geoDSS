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
        
        # todo: merge smarter: only set values when in settings so that definition overrules settings
        if settings:
            for key, value in settings.items():
                self.definition[key] = value

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
