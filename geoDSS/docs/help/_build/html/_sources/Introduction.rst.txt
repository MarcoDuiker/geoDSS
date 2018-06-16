============
Introduction
============

So what is geoDSS and who is it meant for?
------------------------------------------

geoDSS is a tool aimed at non-programmers wanting to run sets of automated tests, mostly (but not necessarily) in the geo-spatial domain.
Running a set of automated tests results in a report, often in html-format.

So typically a GIS-specialist would create something that geocodes an address and test if this address is within an area of interest.

geoDSS can run in batch mode and scheduled mode, often resulting in reports in .csv format. geoDSS can be run from the command line, as a cgi or wsgi web application. 
Furthermore geoDSS can be imported as a Python module and then be used with a few simple lines of Python. 

As geoDSS is very flexible it is also possible to monitor webservices, batch convert addresses to coordinates and much more.

On top of that geoDSS is very extendable so that a programmer (or someone who can copy, paste and adapt Python code) can add to geoDSS capabilities.
Eg. add tests and reporters.


Getting help
------------

All code lives on GitHub, where you can find this documentation and API documentation providing all the details.

On GitHub you'll also find an issues page for reporting bugs.

geoDSS has an examples folder with a lot of examples to get you started.


Concepts
--------

Before putting geoDSS to good use you need to know a few basic concepts used in geoDSS:

Subject
^^^^^^^

A :ref:`subject <subject>` is evaluated against the :ref:`rules`. Eg. an address or a coordinate.

Rule
^^^^

:ref:`rules` can be of different types: :ref:`tests` or :ref:`processors`.

A test will either evaluate to `True` or `False`. When the test evaluates to `True` something will be added to the report.

A processor alters the subject. Eg. put a buffer around a point, or geocode an address.
    
    
Rule set
^^^^^^^^

A set of :ref:`rules`, executed in order.
    
Report
^^^^^^

A :ref:`report` is a collection of things reported by the :ref:`rules` in the :ref:`rule set <ruleset>`. Most of the time this will be a html page. 
    
    

Getting started
---------------

Probably the easiest way to try geoDSS is firing up the integrated webserver by executing `serve_cgi` and then browse to:


http://localhost:8000/cgi-bin/interfaces.py?form=geoDSS/examples/forms/basic.yaml&template=geoDSS/examples/forms/basic_template.html&output_format=html


The next thing to try is to execute an example from the command line (in a terminal):

``./geoDSS examples/rule_sets/unit_test.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)" }'``

Probably now it's best to go to the use cases section of this help. There you'll find some more elaborate examples and recipes.





