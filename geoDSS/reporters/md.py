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

    if 'html_wrapper' in kwargs:
        html_wrapper = kwargs['html_wrapper']
    else:
        html_wrapper = u'''
        <html>
        <head>
            <title>geoDSS</title>
            <style>
                body {width: 600px; margin: 0; padding-left: 5%; font-size: 80%; line-height: 1.5;font-family: arial;color: #333333;}
                article, aside, figcaption, figure, footer, header, nav, section {display: block;}
                pre {padding-left: 6px; border-left-style: solid; border-color: gray; border-width: 8px;}
                h1, h2, h3, h4 {margin: 1em 0 0em; line-height: 1.25;background-color: white;}
                h1 {font-size: 2em;padding:10px; padding-top:50px; border-style: solid; border-color: black; border-width: 1px; border-radius: 5px;}
                h2 {font-size: 1.5em;margin-top: 0;padding-top: 1.5em; border-bottom-style: solid; border-color: black; border-width: 2px;}
                h3 {font-size: 1.2em;}
                ul, ol {margin: 1em 0; padding-left: 40px;}
                p, figure {margin: 1em 0; }
                a img {border: none;}
                sup, sub {line-height: 0;}
                .tagline {margin-top: 50px; padding-top:10px; text-align: right;font-size: 70%; color: gray; border-top-style: solid; border-color: gray; border-width: 1px;}
                .content {background-color: rgba(250,250,250,50);}
                img {border: 2px solid gray;}
                img[alt='Centered_map_small'] {outline-width: 5px; outline-style: solid; outline-color: rgba(200,0,0,.5); outline-offset: -90px; }
                img[alt='Centered_map_medium'] {outline-width: 5px; outline-style: solid; outline-color: rgba(200,0,0,.5); outline-offset: -190px; }
                img[alt='Centered_map_large'] {outline-width: 5px; outline-style: solid; outline-color: rgba(200,0,0,.5); outline-offset: -340px; }
            </style>
        </head>
        <body>
            <div class="content">
                ___content_goes_here___
            </div>
            <div class='tagline'>Powered by <a href="https://github.com/MarcoDuiker/geoDSS">geoDSS</a></div>
        </body>'''

    obj = rule_set

    markdown = u''
    markdown = markdown + obj.definition['title'] + '\n'
    markdown = markdown + '=' * len(obj.definition['title']) + '\n'
    markdown = markdown + '\n'
    if len(obj.definition['description']):
        markdown = markdown + '_' + obj.definition['description'] + '_' + '\n'
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
        return html_wrapper.replace('___content_goes_here___',md_lib.markdown(markdown))
    else:
        return markdown

def rule_reporter(rule):
    '''
    reports on a rule using markdown
    '''

    obj = rule

    markdown = ''

    if obj.definition['report']:
        markdown = markdown + obj.definition['title'] + '\n'
        markdown = markdown + '-' * len(obj.definition['title']) + '\n'
        markdown = markdown + '\n'
        if len(obj.definition['description']):
            markdown = markdown + '_' + obj.definition['description'] + '_' +  '\n'
            markdown = markdown + '\n'
        if obj.executed:
            if hasattr(obj,'decision'):
                if obj.decision:   
                    for row in obj.result:
                        markdown = markdown + '- ' + row + '\n'
                else:
                    markdown = markdown + 'Test decision is: **False**' + '\n'
            else:
                if obj.result:
                    for row in obj.result:
                        markdown = markdown + row + '\n'
        else:
            if obj.result:
                markdown = markdown + '**Error**: test is not executed: ' + '\n'
                for row in obj.result:
                    markdown = markdown + row + '\n'
            else:
                markdown = markdown + '**Error**: test is not executed.' + '\n'
    return markdown
