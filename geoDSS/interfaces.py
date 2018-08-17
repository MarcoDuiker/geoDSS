#!/usr/bin/env python
#!C:/Python27/python.exe -u
# -*- coding: utf-8 -*-

'''
This example code provides several interfaces to geoDSS:

- command line
- cgi
- wsgi

Of course this example is functional, but might be improved on with eg. better cgi handling,
more error checking, logging and communication with the user.

Enable citg (cgi)
-----------------

Adapt the global variable ENABLE_CGTIB to enable cgitb.

**NOTICE**
>cgitb doesn't always play nice with apache: (https://bugs.python.org/issue8704)

**WARNING**
>don't enable cgitb in a production environment!

>and remember: don't enable cgitb in a production environment!

Fetch remote rule_set files
---------------------------

Adapt the global variable ENABLE_NON_LOCAL_RULE_SET_FILES to enable fetching of rule_set files from a remote host.

**WARNING**    
>Do not enable this in a production environment with the standard geoDSS processors and tests.

>You allow the execution of arbitrary SQL commands in your database.

>And probably some more ugly stuff as allowing the user to create an open proxy. 


Logging
-------

Adapt the global variable DEBUG_LEVEL to control what's written to stderr. 

This setting only affects interfaces.py. geoDSS utilyzes a logger which is configured via the rule_set_file.
When using cgi, most of the time you'll find the things written to stderr in your webservers logs.
You can set 
>DEBUG_LEVEL = {False | "DEBUG"}
'''

ENABLE_CGTIB = False
ENABLE_NON_LOCAL_RULE_SET_FILES = False
DEBUG_LEVEL = "DEBUG"

import argparse
import cgi
import json
import logging
import os
import sys
import traceback

try:
    import exceptions
except:
    pass

if ENABLE_CGTIB:
    import cgitb

# make sure we can import the package when run as script
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import geoDSS 
from geoDSS import loaders
from geoDSS import ui_generators

def sanitize_headers(headers):
    '''
    removes hop-by-hop headers as these are not supported by wsgi.
    '''

    hop_by_hop_headers = ('connection','keep-alive','public','proxy-authenticate','transfer-encoding','upgrade')
    keys = [x.lower() for x in headers.keys()]
    for h in hop_by_hop_headers:
        if h in keys:
            headers.pop(h)
    return headers

def load_execute_report(params):
    ''' 
    main entrypoint

    command line, cgi and wsgi interfaces end up here.
    
    `params`     a CGI field storage object.
    '''

    
    mime = 'text/plain'
    try:
        output_format = params['output_format'][0]
        if output_format in ['html']:
            mime = 'text/html'
        if output_format in ['pdf']:
            mime = 'application/pdf'
            #mime = 'text/plain'
        elif output_format in ['markdown']:
            mime = 'text/plain'
    except:
        output_format = 'markdown'

    response_headers = {'Content-Type': mime}
    status = '400 Bad Request'
    
    if 'form' in params:        
        form_definition = params['form'][0]
        template = None
        if 'template' in params:
            template = params['template'][0]
        try:
            data = geoDSS.ui_generators.form.generate(form_yaml = form_definition, template = template)
        except Exception as e:
            if DEBUG_LEVEL:
                sys.stderr.write("geoDSS: Could not generate form with error: %s \n" % str(e))
                sys.stderr.write(traceback.format_exc())
            return status, response_headers, "Could not generate form with error: " + str(e)
            
    elif 'rule_set_file' in params:
        try:
            subject = json.loads(params['subject'][0])
        except Exception as e:
            if DEBUG_LEVEL:
                sys.stderr.write("geoDSS: Could not parse subject with error: %s \n" % str(e))
                #sys.stderr.write("geoDSS: " + params['subject'][0])
            return status, response_headers, "Could not parse subject with error: " + str(e)

        rule_set_file = params['rule_set_file'][0]
        base_name,extension = os.path.splitext(rule_set_file)

        loader_module = loaders.yaml_loader
        if extension == '.json':
            loader_module = loaders.json_loader

        if ENABLE_NON_LOCAL_RULE_SET_FILES:
            try: 
                rule_set_file = params['protocol'][0] + '://' + rule_set_file
            except:
                pass

        try:
            r = geoDSS.rules_set(rule_set_file, loader_module)
        except Exception as e:
            if DEBUG_LEVEL:
                sys.stderr.write("geoDSS: Could not load rule_set with error: %s \n" % str(e))
                sys.stderr.write(traceback.format_exc())
            return status, response_headers, "Could not load rule_set with error: " + str(e)
        
        try:
            r.execute(subject)
        except Exception as e:
            if DEBUG_LEVEL:
                sys.stderr.write("geoDSS: Could not evaluate rule_set with error: %s \n" % str(e))
                sys.stderr.write(traceback.format_exc())
            return status, response_headers, "Could not evaluate rule_set with error: " + str(e)

        try:
            sys.stderr.write("trying to generate a report with output format: " + output_format)
            data = r.report(output_format = output_format)
        except Exception as e:
            if DEBUG_LEVEL:
                sys.stderr.write("geoDSS: Could not report on rule_set with error: %s \n" % str(e))
                sys.stderr.write(traceback.format_exc())
            return status, response_headers, "Could not report on rule_set with error: " + str(e)
            
    else:
        data = "You are almost there... Please specify a form to load or a rule_set to proces."

    status = '200 OK'
    response_headers["Content-Length"] = str(len(data))

    return status, response_headers, data


def application(environ, start_response):
    '''
    WSGI entry method: called by WSGI framework.
    '''

    if ENABLE_CGTIB:
        cgitb.enable()
        if DEBUG_LEVEL:
            sys.stderr.write("geoDSS: enabling cgitb. \n")

    if DEBUG_LEVEL:
        sys.stderr.write('geoDSS: WSGI environ=%s \n' % str(environ))

    if "REQUEST_METHOD" in environ and environ['REQUEST_METHOD'] == 'POST':
        query_string = environ['wsgi.input']
    elif "REQUEST_METHOD" in environ and environ['REQUEST_METHOD'] == 'GET':
        query_string = environ['QUERY_STRING']
    else:
        if DEBUG_LEVEL:
            sys.stderr.write("geoDSS: Only HTTP POST and GET are supported. \n")
        raise NotImplemented('Only HTTP POST and GET are supported')
    params = cgi.parse_qs(query_string, keep_blank_values=True)

    status, response_headers, data = load_execute_report(params)
    headers = sanitize_headers(response_headers)
    start_response(status, headers.items())
    return [data]


def cgi_application(params):
    '''
    CGI entry method: called locally.

    example:  `http://localhost:8000/cgi-bin/geodss.cgi?output_format=html&rule_set_file=geoDSS/geoDSS/examples/rule_sets/bag_geocoder_test.yaml&subject={%22postcode%22:%20%224171KG%22,%20%22huisnummer%22:%20%2274%22}`
    '''

    status, response_headers, data = load_execute_report(params)
    response_headers = sanitize_headers(response_headers)               # this one not necessary, but it keeps in line with the wsgi interface
    headers = '\r\n'.join( ["%s: %s;" % (key, value) for key, value in response_headers.iteritems()] ) + '\r\n' + '\r\n'
     
    sys.stdout.write(headers)
    sys.stdout.write(data)


# Get form/query params (CGI)
parameters = cgi.FieldStorage(keep_blank_values = True)
param_count = len(parameters.keys())
if param_count > 0 and 'wsgi.version' not in parameters and 'REQUEST_METHOD' in os.environ:

    # We are called as CGI: handle with CGI function

    if ENABLE_CGTIB:
        if DEBUG_LEVEL:
            sys.stderr.write("geoDSS: enabling cgitb. \n")
        cgitb.enable()
    if os.environ['REQUEST_METHOD'] == "GET":
        query_string = os.environ['QUERY_STRING']
        params = cgi.parse_qs(query_string, keep_blank_values=True)
    elif os.environ['REQUEST_METHOD'] == "POST":
        params = {}
        for param in parameters.keys():
            try:
                params[param] = parameters.getList(param)
            except:
                if DEBUG_LEVEL:
                    sys.stderr.write("geoDSS: Received POST data in a way not supported yet. Doing a guess. \n")
                params[param] = [parameters.value]
    else:
        if DEBUG_LEVEL:
            sys.stderr.write("geoDSS: Only HTTP POST and GET are supported. \n")
        raise NotImplemented('Only HTTP POST and GET are supported')
    cgi_application(params)

elif __name__ == '__main__':
    '''
    this script is invoked from command line

    >example:   `./geoDSS examples/rule_sets/unit_test.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)" }'`

    >           `./geoDSS examples/rule_sets/various.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)", "brzo": "true" }'`
    '''

    parser = argparse.ArgumentParser(description = 'Invoke geoDSS from command line using the default markdown reporter with output_format markdown.',
                                     epilog =      '''Example: ./geoDSS examples/rule_sets/unit_test.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)" }' ''')
    parser.add_argument("rule_set_file",                            help = 'The file containing the rule set.')
    parser.add_argument("subject",                                  help = 'Either a JSON-string defining a python dict containing a subject or a path to a file containing such a JSON-string.')
    parser.add_argument("--output_file",                            help = 'An output file to write the results to. If not given, output is to stdout.')
    parser.add_argument("--file_mode", default = "wb" , 
                                       choices=('wb', 'wt', 'ab', 'at'), 
                                                                    help = 'Python file mode. mode starting with "a" will append, starting with "w" will overwrite.' )
    args = parser.parse_args()

    if os.path.exists(args.subject):
        with open(args.subject, 'r') as f:
            subject_string = f.read()
    else:
        subject_string = args.subject

    params = {  'rule_set_file': [args.rule_set_file],
                'subject':       [subject_string],
                'output_format': ['markdown']}

    status, response_headers, data = load_execute_report(params)
    if args.output_file:
        with open(args.output_file,args.file_mode) as f:
            f.write(data)
    else:
        print(data)

else:

    # Standard WSGI: do nothing as WSGI entry-function 'application' will be invoked

    pass

