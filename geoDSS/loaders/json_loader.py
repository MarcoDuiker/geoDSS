# -*- coding: utf-8 -*-
'''
This rule_set loader loads a rule_set from a json file from the local file system.
If rule_set_file starts with http(s):// rule_Set_file is regarded as an url and the json will be fetched from there.
'''

import json
import requests

def load_rule_set(rules_set_file, **kwargs):
    '''
    Load rules set from json.

    rules_set_file is expected to be a file name of a file containing a rules set definition in json format.

    Example
    -------

        { "name": "set 1 json"
          "title": "Rule set doing a unit like test",
          "description": "use the unit test to test the framework, demonstrating the json loader on the go.",
          "logging": {
            "level": "DEBUG"
          },
          "rules": [
            {
              "unit_test": {
                "report_template": "Action should be taken",
                "type": "tests.unit_test",
                "description": "unit test testing",
                "title": "unit test"
              }
            },
            {
              "postgis_unit_test": {
                "type": "processors.postgis_unit_test",
                "db": {
                  "dbname": "gisdefault"
                },
                "description": "unit test by buffering subject geometry with distance 1",
                "title": "processor unit test"
              }
            }
          ]
        }

    **kwargs is not used in this loader and only inserted here as an example for extending the loaders.

    '''

    # todo: we might need something like: input_file = codecs.open("some_file.txt", mode="r", encoding="utf-8")
    if rules_set_file.startswith('http://') or rules_set_file.startswith('https://'):
        response = requests.get(rules_set_file)
        if response.status_code == requests.codes.ok:
            return json.loads(response.text)
    else:
        with open(rules_set_file) as stream:
            return json.load(stream)
