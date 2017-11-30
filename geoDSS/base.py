# -*- coding: utf-8 -*-
'''
The base module provides the rules_set class. This class is all you need to work with to run your testing.

Example:
>>>import geoDSS                                                        # be sure this is possible by installing geoDSS 
>>>                                                                     # or invoking this from the right working dir

>>>r = geoDSS.rules_set('geoDSS/examples/rule_sets/unit_test.yaml')     # and then check this path as well
>>>r.execute( subject = {  'result': True,
...                        'geometry': 'SRID=28992;POINT((125000 360000))'
...                     })
>>>r.report()
'''

import copy
import datetime
import locale
import os
import sys
from abc import ABCMeta, abstractmethod
try:
    import exceptions
except:
    pass

import logging
import logging.handlers

import loaders
import processors
import tests
import reporters



class rules_set(object):
    '''
    container object for a set of rules
    '''

    def __init__(self, rules_set_file, loader_module = loaders.yaml_loader, **kwargs):
        '''
        Reads the rules_set with the load_rule_set method of the loader_moduler
        If not specified the dafault yaml loader is used.

        rules_set_file is expected file containing the rules set.
        '''

        self.definition = None
        self.definition = loader_module.load_rule_set(rules_set_file)
        if not 'title' in self.definition.keys():
            self.definition['title'] = self.definition['name'] 
        if not 'description' in self.definition.keys():
            self.definition['description'] = '' 
        if not 'settings' in self.definition.keys():
            self.definition['settings'] = None
        if not 'logging' in self.definition.keys():
            self.definition['logging'] = {}

        self.logger = self._setup_logging()

        self.rules = []
        dss = sys.modules[__name__]
        for rule in self.definition['rules']:
            name = rule.keys()[0]
            definition = rule[name]
            _group, _class = definition['type'].split('.',2)
            if hasattr(dss, _group):
                _group = getattr(dss, _group)
            else:
                self.logger.error('The group %s is not defined yet.' % _group)
                raise exceptions.NotImplementedError('The group %s is not defined yet.' % _group)
            if hasattr(_group, _class):
                # the class is in a module eg unit_test.unit_test
                _group = getattr(_group, _class)
                test_to_add = getattr(_group, _class)
                self.logger.debug("Adding test with name: %s" % name)
                self.rules.append(test_to_add(name, definition, logger = self.logger, settings = self.definition['settings']))
            else:
                self.logger.error('The type %s is not defined yet.' % definition['type'])
                raise exceptions.NotImplementedError('The type %s is not defined yet.' % definition['type'])

    def _setup_logging(self):
        '''
        sets up the logger
        '''

        logger = logging.getLogger()
        logger.name = self.definition['name']
        log_level = logging.INFO
        if 'level' in self.definition['logging'].keys():
            log_level = logging.getLevelName(self.definition['logging']['level'])
        logger.setLevel(log_level)
        log_format = '%(asctime)s %(name)-12s %(levelname)-7s  %(message)s'
        if 'format' in self.definition['logging'].keys():
            log_format = self.definition['logging']['format']
        formatter = logging.Formatter( log_format )
        if 'file' in self.definition['logging'].keys():
            hdlr = logging.handlers.RotatingFileHandler(self.definition['logging']['file'], maxBytes= 1 * 1000000, backupCount=5)
        else:
            hdlr = logging.StreamHandler()
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)

        logger.info("Logger is activated on level: %s" % logging.getLevelName(log_level) )
        return logger

    def execute(self, subject):
        '''
        Executes processors and tests in the rules_set.

        this methoud should be called BEFORE the report method.

        subject is expected to be a dict which is passed to each rule.
        '''

        self.result = []                                                 # the rule_set has it's own result we can report on; we fill it with the subjects
        self.result.append(copy.deepcopy(subject))                       # add the first subject to the result

        self.logger.info("Start execution of rules")
        self.logger.debug('First subject: ' + str(subject))

        for rule in self.rules:
            self.logger.debug('Executing rule "%s" with subject "%s"' % (str(rule.name), str(subject)))
            result = rule.execute(subject)
            if result:
                self.result.append(copy.deepcopy(subject))               # and add each subject to the rule_set_result as well
                subject = result
            if not result:
                self.logger.info('Rule "%s" returned False to end execution.' % str(rule.name))
                break
        self.logger.info("Finished execution of rules")

    def report(self, reporter_module = reporters.md, **kwargs):
        '''
        Report the result of the rules.

        this method should be called AFTER the execute method.

        reporter_module is the module used to report. 
            This module should have a class 'rule_set_reporter' which is called with the supplied kwargs.

        If reporter_module is not supplied the reporters.md module is used as a default.
            The reporters.md method 'rule_set_reporter' accepts an optional output_format parameter which is expected to be one of:
                - 'markdown'    (default)
                - 'html'
        '''

        return reporter_module.rule_set_reporter(self, **kwargs)


