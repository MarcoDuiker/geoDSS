# -*- coding: utf-8 -*-

try:
    import markdown as md_lib
except:
    import pymarkdown as md_lib
import yaml

# todo: less naive implementations

def rule_set_reporter(rule_set, output_format = 'markdown', **kwargs):
    '''
    reports on a rule set using markdown or html

    output format is expected to be one of:
    - 'markdown' (default)
    - 'html'

    **kwargs is not used in this reporter and only inserted here as an example for extending the reporters
    '''

    # todo: add what to report as parameter?

    obj = rule_set

    markdown = u''
    markdown = markdown + obj.definition['title'] + '\n'
    markdown = markdown + '=' * len(obj.definition['title']) + '\n'
    markdown = markdown + '\n'
    markdown = markdown + obj.definition['description'] + '\n'
    markdown = markdown + '\n'
    markdown = markdown + 'Subject' + '\n'
    markdown = markdown + '-------' + '\n'
    markdown = markdown + 'Started processing with subject: ' + '\n\n'
    markdown = markdown + '\t' + yaml.safe_dump(obj.result[0],default_flow_style=False).replace('\n','\n\t') + '\n'
    markdown = markdown + '\n'
    markdown = markdown + 'Results' + '\n'
    markdown = markdown + '=======' + '\n'
    markdown = markdown + '\n'

    for rule in rule_set.rules:
        markdown = markdown + rule_reporter(rule) + '\n'

    if output_format == 'html':
        return md_lib.markdown(markdown)
    else:
        return markdown

def rule_reporter(rule):
    '''
    reports on a rule using markdown
    '''

    obj = rule

    markdown = ''
    markdown = markdown + obj.definition['title'] + '\n'
    markdown = markdown + '-' * len(obj.definition['title']) + '\n'
    markdown = markdown + '\n'
    markdown = markdown + obj.definition['description'] + '\n'
    markdown = markdown + '\n'
    if obj.executed:
        if hasattr(obj,'decision'):
            if obj.decision:   
                for row in obj.result:
                    markdown = markdown + '- ' + row + '\n'
            else:
                markdown = markdown + 'Test decision is: False' + '\n'
        else:
            if obj.result:
                for row in obj.result:
                    markdown = markdown + row + '\n'
    else:
        if obj.result:
            markdown = markdown + 'Error: test is not executed: ' + '\n'
            for row in obj.result:
                markdown = markdown + row + '\n'
        else:
            markdown = markdown + 'Test is not executed' + '\n'
    return markdown
