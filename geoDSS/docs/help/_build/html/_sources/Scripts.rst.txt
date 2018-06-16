=======
Scripts
=======

GeoDSS comes with a few scripts which use the geoDSS module to run geoDSS in several useful ways. 

interfaces.py
-------------

``interfaces.py`` provide a command line interface to geoDSS as well as cgi and wsgi interfaces.

Typing ``interfaces.py`` without arguments gives some help. More help can be found in the `API documentation <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/index.html>`_.

scheduled.py
------------

``scheduled.py`` runs geoDSS on a schedule, optionally for a preset amount of time.

Typing ``scheduled.py`` without arguments gives some help. More help can be found in the `API documentation <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/index.html>`_.

batch.py
--------

``batch.py`` runs several subjects provided in a .csv file against a rule set. Of course, this only works for subjects which can be defined by simple key-value pairs. 

The keys are taken from the column names, the values from the corresponding columns.

Typing ``batch.py`` without arguments gives some help. More help can be found in the `API documentation <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/index.html>`_.

serve_cgi
---------

serve_cgi starts a webserver on localhost port 8000. This webserver demonstrates how to use geoDSS as a cgi application.

Once the webserver is started you can run an example by browsing to:

http://localhost:8000/cgi-bin/interfaces.py?form=geoDSS/examples/forms/basic.yaml&template=geoDSS/examples/forms/basic_template.html&output_format=html

This actually executues interfaces.py. More information on the usage of interfaces.py is on this page and in the `API documentation <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/index.html>`_.

On windows you can start the webserver by executing: 

``serve_cgi.bat``


On most other operating systems you can either run 

``serve_cgi.sh`` 

or 

``serve_cgi.py``

If that doesn't work you probably need to do: 

``python serve_cgi.py``