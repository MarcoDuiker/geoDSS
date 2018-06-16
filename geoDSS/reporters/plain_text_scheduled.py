# -*- coding: utf-8 -*-

import datetime

try:
    import exceptions
except:
    pass

def rule_set_reporter(rule_set, output_format = 'plain_text', **kwargs):
    '''
    Reports on a rule set using plain text. This reporter writes the first result of 
    each rule in the rule set, then the second and so on till results are exhausted.
    
    This preserves order if the rule set is executed multiple times, eg. when running
    geoDSS scheduled.
    
    Make sure each rule has the same number of results!

    Only results are reported. No titles, no subject, no failed tests!
    
    The description of the rule set can be used to generate a header.
    
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

    result = True
    result_number = 0
    while not result == False:
        for rule in rule_set.rules:
            result = rule_reporter(rule, result_number)
            if not result == False:
                txt = txt + result
        result_number = result_number + 1

    return txt

def rule_reporter(rule, result_number = 0):
    '''
    Reports on a rule using plain text.
    '''

    obj = rule

    if obj.definition['report']:
        if obj.executed:
            if (hasattr(obj,'decision') and obj.decision) or obj.result:
                try:
                    return obj.result[result_number] + '\n'
                except:
                    return False
                    
    return None
