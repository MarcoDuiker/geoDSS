#!/usr/bin/env python
#!C:/Python27/python.exe -u
# -*- coding: utf-8 -*-

'''
With servi_cgi it is easy to bring up a webserver listening on port 8000
to start using geoDSS via a webinterface. 
Furthermore this serves as an example for how to include geoDSS in
webinterfaces.

Warning
-------

**serve.cgi is not meant for production use.**

**Probably you don't want to expose serve.cgi to the internet.**

Usage
-----

On windows start serve_cgi by running `serve_cgi.bat`.

On Linux start serve_cgi by running `serve_cgi.sh` or `serve_cgi.py`.

Once you've started serve_cgi you can open a browser and browse to one of the examples:
>http://localhost:8000/cgi-bin/interfaces.py?form=../geoDSS/examples/forms/basic.yaml&template=../geoDSS/examples/forms/basic_template.html&output_format=html
>http://localhost:8000/cgi-bin/interfaces.py?output_format=html&rule_set_file=../geoDSS/examples/rule_sets/pdok_locatieserver.yaml&subject={"postcode": "4171KG", "huisnummer": "74"}}

'''

import CGIHTTPServer
import os

# default port and address to listen to
port = 8000
address = ''

class MyCGIHTTPRequestHandler(CGIHTTPServer.CGIHTTPRequestHandler):
    def is_python(self, path):
        # Extend as to enable .cgi files to be recognized (Windows issue)
        head, tail = os.path.splitext(path)
        return tail.lower() in (".py", ".pyw", ".cgi")


def main():

    server = CGIHTTPServer.BaseHTTPServer.HTTPServer((address, port), MyCGIHTTPRequestHandler)
    help = '\nHTTP and CGI server starting, browse to http://127.0.0.1:%i/cgi-bin/interfaces.py, shutdown with Ctrl-C' % port
    help = help + '\nExample: http://localhost:8000/cgi-bin/interfaces.py?output_format=html&rule_set_file=../geoDSS/examples/rule_sets/pdok_locatieserver.yaml&subject={"postcode": "4171KG", "huisnummer": "74"}'
    try:
        print(help)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()
