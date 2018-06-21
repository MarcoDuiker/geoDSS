geoDSS
======

geoDSS is a simple yet very extendable library to create automatic testing of a subject (argument) against rules and then report on the results.

geoDSS is a simple rule engine with a focus on geospatial rules.

The library can be imported, or used via the interfaces scripts providing interfaces for:

- command line
- cgi
- wsgi


Concepts
--------

geoDSS passes the subject (argument) to the rules defined in a rule_set, one by one in order. A rule can be a:

- processor
  a processor alters the subject. Eg. buffers a geometry with 100 meters. So the next test or processor will work on the altered subject.
- test
  a test result is either `True` or `False`. When `True` the given `report_template` will be converted to a report string and added to the report. 
  Most   of the time the reported string will be the same as the `report_template`. But you can add `{a_parameter}` to a `report_template` and then substitute this parameter by a value. Eg. if you test if a subject is near a municipality you can substitute `{a_parameter}` by the name of the municipality.

The rule_set must be loaded from file (yaml or json). The subject (argument) can be passed in to evaluate the rules. Loading of the rule_set, passing in the subject and evaluet the rules can be done via a simple Python script, command line, cgi or wsgi.
  
The report will be in markdown, or if you prefer, in html. The report will list all report strings, prepended with a report on the rule_set and the subject.


Install
-------

After downloading geoDSS from git (optionally unpack or unzip) you can build and install with:

	python setup.py build
	python setup.py install
	
Alternatively you can also create an installable first, and install that with `pip`:

	python setup.py bdist_wheel
	
And then do:

	pip install <the_wheel_file_you_created.whl>
	
####Requirements

Processors and tests can have dependencies on non-standard Python libraries. When these are not installed, the test or processor won't run, but other tests and processors will.

The following libraries are not optional:

- yaml
- markdown
- requests

Most off the time you'll also want to install:

- psycopg2
- json
- xml

	
Documentation
-------------

The [API-docs](https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/index.html) provide useful information for both users and developers.

Especially useful are:
>https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/interfaces.m.html

>https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/base.m.html

>https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/tests/index.html

>https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/processors/index.html

Help you can find in the [help pages](https://marcoduiker.github.io/geoDSS/geoDSS/docs/help/_build/html/index.html) .
	

Quick Start
-----------

To use the standard offering, first create a rule set in yaml (or json) format (you'll find this in the `examples` folder so you don't even have to bother to copy and paste):

	name: various_rules_test
	title: Doing some different tests
	description: ""
	rules:
	- remark:
	    type: tests.remark
	    title: Be aware!
	    description: ""
	    report_template: description cannot be empty
	- unit_test:
	    type: tests.unit_test
	    title: unit test
	    description: unit test testing
	    report_template: Action should be taken
	- postgis_unit_test:
	    type: processors.postgis_unit_test
	    title: processor unit test
	    description: unit test by buffering subject geometry with distance 1
	    db:
		dbname: gisdefault
	- brzo:
	    type: tests.key_value_compare
	    title: BRZO bedrijf
	    description: ""
	    key: brzo
	    value: "true"
	    operator: "=="
	    report_template: Doorsturen aan RWS
	- postgis_unit_test:
	    type: tests.postgis_spatial_select
	    title: Gemeenten binnen 10 km van de aanvraag
	    description: ""
	    schema: public
	    table: gem_2009_gen
	    relationship: ST_DWithin
	    parameters: 
	    - "subject.geometry"
	    - "wkb_geometry"
	    - "30000"
	    report_template: Doorsturen naar B&W van gemeente {gm_naam}
	    db:
			dbname: gisdefault
			
then use the following script to run a subject against the rules and see the report in markdown format (you'll find this script in the `examples` folder as well):

	import geoDSS            # be sure this is possible by installing geoDSS 
		                     # or invoking this from the right working dir

	r = geoDSS.rules_set('geoDSS/examples/rule_sets/unit_test.yaml')        # and then check this path as well
	r.execute( subject = {  'result': True,
		                    'geometry': 'SRID=28992;POINT((125000 360000))'
		             })
	print(r.report())
	
alternatively you can execute from command line with something like:

	python interfaces.py examples/rule_sets/various.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)", "brzo": "true" }'
	
if your on Linux you might want to add a symlink to interfaces.py so that you can do something like:

	./geoDSS examples/rule_sets/various.yaml '{"result": true, "geometry": "SRID=28992;POINT(125000 360000)", "brzo": "true" }'
	
	

	
Extend
------

A few useful tests and processors are provided. The most notable ones being:

- `processors.postgis_processing`
- `tests.postgis_spatial_select`
- `tests.wfs2_SpatialOperator`

You should be able to do some useful work with that. But you can easily add your own tests and processors.


Actually, you can extend the:
 
- `tests`
- `processors`
- `reporters` 
- `loaders`
- `ui_generators`

You'll probably want to extend the first two of this list to begin with. As the existing tests and processors are heavily documented it won't be a problem to add a new test or processor by mimicking one of the existing ones.

Probably the easiest to understand and extend is `tests.remark`.

Just don't forget to add your newly created test or processor to the `imports` in `__init__.py`. Otherwise your new addition won't show up!

