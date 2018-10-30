# -*- coding: utf-8 -*-
'''
The base module provides the rules_set class. This class is all you need to work with to run your testing.

Example
-------

    import geoDSS                                                        # be sure this is possible by installing geoDSS 
                                                                         # or invoking this from the right working dir

    r = geoDSS.rules_set('geoDSS/examples/rule_sets/unit_test.yaml')     # and then check this path as well
    r.execute( subject = {  'result': True,
                            'geometry': 'SRID=28992;POINT((125000 360000))'
                         })
    print(r.report())
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
    Container object for a set of rules.
    '''

    class Rules(object):
        '''
        A convenience object to stick rules on.

        Especially handy for the evaluate test so that we can write nice things in the rule_set file like 'rules.test1'
        '''

        pass

        # todo: add an iterator or __getitem__ and use this class instead of the list (keep order!)


    def __init__(self, rules_set_file, loader_module = loaders.yaml_loader, **kwargs):
        '''
        Reads the rules_set with the load_rule_set method of the loader_moduler.

        If not specified the default yaml loader is used.

        `rules_set_file` is expected to be a file containing the rules set.
        '''

        dss = sys.modules[__name__]

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
        if not 'break_on_true' in self.definition.keys():
            self.definition['break_on_true'] = False
        if not 'break_on_false' in self.definition.keys():
            self.definition['break_on_false'] = False

        self.logger = self._setup_logging()

        if not 'reporter' in self.definition.keys():
            self.reporter_module = reporters.md
        else:
            _group, _class = self.definition['reporter'].split('.',2)
            if hasattr(dss, _group):                                        # this allows for reporters outside the reporters module
                _group = getattr(dss, _group)
            else:
                self.logger.error('The module %s is not defined yet.' % _group)                         
                raise exceptions.NotImplementedError('The module %s is not defined yet. Did you mean to use the reporters module?' % _group)
            if hasattr(_group, _class):
                self.reporter_module = getattr(_group, _class)
                self.logger.debug("Selecting reporter %s" % self.reporter_module.__name__)
            else:
                self.logger.error('The reporter %s is not defined yet.' % self.definition['reporter'])
                raise exceptions.NotImplementedError('The reporter %s is not defined yet.' % self.definition['reporter'])

        self.reporter_args = None
        if 'reporter_args' in self.definition.keys():
            self.reporter_args = self.definition['reporter_args']

        self._rules = self.Rules()
        self.rules = []
        for rule in self.definition['rules']:
            name = rule.keys()[0]
            definition = rule[name]
            _group, _class = definition['type'].split('.',2)
            if hasattr(dss, _group):
                _group = getattr(dss, _group)
            else:
                self.logger.error('The module %s is not defined yet.' % _group)
                raise exceptions.NotImplementedError('The module %s is not defined yet.Did you mean to use the tests or processors module?' % _group)
            if hasattr(_group, _class):
                # the class is in a module eg unit_test.unit_test
                _group = getattr(_group, _class)
                test_to_add = getattr(_group, _class)
                self.logger.debug("Adding rule with name: %s" % name)
                self.rules.append(test_to_add(name, definition, logger = self.logger, rules = self._rules, settings = self.definition['settings']))
            else:
                self.logger.error('The type %s is not defined yet.' % definition['type'])
                raise exceptions.NotImplementedError('The type %s is not defined yet.' % definition['type'])


    def _setup_logging(self):
        '''
        Sets up the logger.

        It uses settings from the rule_set file:

            - logging:
              - level                       Python log level. Usually one of: DEBUG, INFO, ERROR (defaults to INFO)
              - format                      Python logging format string. Default: '%(asctime)s %(name)-12s %(levelname)-7s  %(message)s'
              - file                        A writeable file to write the log. This file will be log-rotated.
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

        this method should be called BEFORE the report method.

        `subject`       is expected to be a dict which is passed to each rule.
        '''

        self.result = []                                                 # the rule_set has it's own result we can report on; we fill it with the subjects
        self.result.append(copy.deepcopy(subject))                       # add the first subject to the rule_set result

        self.logger.info("Start execution of rules")
        self.logger.debug('First subject: ' + str(subject))

        for rule in self.rules:
            self.logger.debug('Executing rule "%s" with subject "%s"' % (str(rule.name), str(subject)))
            result = rule.execute(subject)
            setattr(self._rules, rule.name, rule)                        # we add a reference to each executed rule here
            if result:
                self.result.append(copy.deepcopy(subject))               # and add each subject to the rule_set result as well
                subject = result
                if self.definition['break_on_true'] and result.decision:
                    self.logger.info('Rule "%s" evaluated to True and ended execution due to break_on_true being True.' % str(rule.name))
                    break
                if self.definition['break_on_false'] and not result.decision:
                    self.logger.info('Rule "%s" evaluated to False and ended execution due to break_on_false being True.' % str(rule.name))
                    break
            if not result:
                self.logger.info('Rule "%s" returned False to end execution.' % str(rule.name))
                break
        self.logger.info("Finished execution of rules")


    def report(self, **kwargs):
        '''
        Report the result of the rules.

        this method should be called AFTER the execute method.

        The default reporter module is reporters.md.

        if `reporter` is part of the definition of the rule set,
        that reporter will be used.

        if `reporter_args` is part of the definition of the rule set,
         the arguments defined there will be passed to the reporter.
        
        if `output_format` is passed as a parameter to the report function,
        this will overrule the `output_format` defined in `reporter_args`.

        A yaml snippet to illustrate the selection of the markdown reporter with html output:

            name: test_bag_geocoder
            title: Test the BAG geocoder
            description: Test the BAG geocoder by geocoding an address and report the result
            reporter: reporters.md
            reporter_args:
              output_format: html

        If no arguments are defined in the rule set, 
        arguments passed in this report method will be passed to the reporter.

        The 'rule_set_reporter' method in the default reporter reporters.md accepts 
        an optional `output_format` parameter which is expected to be one of:

        - 'markdown'    (default)
        - 'html'
        - 'pdf'
        '''

        if self.reporter_args:
            if 'output_format' in kwargs:
                return self.reporter_module.rule_set_reporter(self, output_format = kwargs['output_format'], **self.reporter_args)
            else:
                return self.reporter_module.rule_set_reporter(self, **self.reporter_args)
        else:
            return self.reporter_module.rule_set_reporter(self, **kwargs)
