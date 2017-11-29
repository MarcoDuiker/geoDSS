# -*- coding: utf-8 -*-
'''
This is the default rule_set loader.

It loads a rule_set from a yaml file.
'''

import yaml

def load_rule_set(rules_set_file, **kwargs):
    '''
    load rules set from yaml

    rules_set_file is expected to be a file name of a file containing a rules set definition in yaml format.

    Example
    -------

    name: set 1
    title: Rule set doing the unit test
    description: use the unit test to test the framework
    rules:
    - unit_test:
        type: tests.unit_test
        title: unit test
        description: unit test testing
        report_template: Action should be taken
    - postgis_unit_test:
        type: processors.postgis_unit_test
        title: processor unit test
        description: unit test by buffering subject geometry with distance 1
        db:
            dbname: gisdefault

    **kwargs is not used in this loader and only inserted here as an example for extending the loaders

    '''

    # todo: we might need something like: input_file = codecs.open("some_file.txt", mode="r", encoding="utf-8")

    with open(rules_set_file) as stream:
        return yaml.load(stream)
