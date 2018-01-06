# -*- coding: utf-8 -*-

import datetime

try:
    import exceptions
except:
    pass

def rule_set_reporter(rule_set, output_format = 'plain_text', **kwargs):
    '''
    Reports on a rule set using plain text.

    Only descriptions and results are reported. No titles, no subject, no failed tests!
    
    The following optional parameters can be passed:

    - `rules_only` (bool):           If set to `True` only the rules will be reported. Defaults to `False`.

    - **kwargs                       Is not used in this reporter and only inserted here as an example for extending the reporters.
    
    The following parameters in the rule_set report will be replaced:
    
    - `{timestamp}`                               The ISO timestamp
    '''

    obj = rule_set
    
    txt = u''
    if len(obj.definition['description']):
        txt = txt + obj.definition['description'].replace('{timestamp}', datetime.datetime.now().isoformat()) + '\n'

    for rule in rule_set.rules:
        txt = txt + rule_reporter(rule)

    return txt

def rule_reporter(rule):
    '''
    Reports on a rule using plain text.
    '''

    obj = rule

    txt = u''

    if obj.definition['report']:
        if len(obj.definition['description']):
            txt = txt + obj.definition['description'] + '\n'
        if obj.executed:
            if (hasattr(obj,'decision') and obj.decision) or obj.result:
                for row in obj.result:
                    txt = txt + row + '\n'

    return txt
