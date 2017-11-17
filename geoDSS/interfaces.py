#!/usr/bin/env python
#!C:/Python27/python.exe -u

'''
This provides several interfaces to geoDSS:
- command line
- cgi
- wsgi
'''

import argparse
import cgi
import cgitb
import json
import os

# make sure we can import the package when run as script
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import geoDSS 

_DEBUG = True

def sanitize_headers(headers):
    '''
    removes hop-by-hop headers as these are not supported by wsgi
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
    command line, cgi and wsgi interfaces end up here
    
    params is a CGI field storage object
    '''

    subject = json.loads(params['subject'][0])
    output_format = params['output_format'][0]
    rule_set_file = params['rule_set_file'][0]

    if output_format in ['html']:
        mime = 'text/html'
    elif output_format in ['markdown']:
        mime = 'text/plain'

    r = geoDSS.rules_set(rule_set_file)
    r.execute(subject)
    data = r.report(output_format = output_format)

    status = '200 OK'
    response_headers = {   
            'Content-type': mime,
            "Content-Length": str(len(data))}

    return status, response_headers, data


def application(environ, start_response):
    '''
    WSGI entry method: called by WSGI framework
    '''

    cgitb.enable()

    if _DEBUG and False:
        print 'WSGI environ=%s' % str(environ)

    if "REQUEST_METHOD" in environ and environ['REQUEST_METHOD'] == 'POST':
        query_string = environ['wsgi.input']
    elif "REQUEST_METHOD" in environ and environ['REQUEST_METHOD'] == 'GET':
        query_string = environ['QUERY_STRING']
    else:
        raise NotImplemented('Only HTTP POST and GET are supported')
    params = cgi.parse_qs(query_string, keep_blank_values=True)

    status, response_headers, data = load_execute_report(params)
    headers = sanitize_headers(response_headers)
    start_response(status, headers.items())
    return [data]


def cgi_application(params):
    '''
    CGI entry method: called locally
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
    cgitb.enable()
    if os.environ['REQUEST_METHOD'] == "GET":
        query_string = os.environ['QUERY_STRING']
        params = cgi.parse_qs(query_string, keep_blank_values=True)
    elif os.environ['REQUEST_METHOD'] == "POST":
        params = {}
        for param in parameters.keys():
            params[param] = parameters.getList(param)
    else:
        raise NotImplemented('Only HTTP POST and GET are supported')
    cgi_application(params)
elif __name__ == '__main__':
    #this script is invoked from command line

    #example:   ./geoDSS examples/rule_sets/unit_test.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)" }'
    #           ./geoDSS examples/rule_sets/various.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)", "brzo": "true" }'

    parser = argparse.ArgumentParser(description = 'Invoke geoDSS from command line using the default markdown reporter with output_format markdown.',
                                     epilog =      '''Example: ./geoDSS examples/rule_sets/unit_test.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)" }' ''')
    parser.add_argument("rule_set_file", help = 'The file containing the rule set')
    parser.add_argument("subject",       help = 'Either a JSON-string defining a python dict containing a subject or a path to a file containing such a JSON-string')
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
    print
    print
    print(data)
else:
    # Standard WSGI: do nothing as WSGI entry-function 'application' will be invoked
    pass

