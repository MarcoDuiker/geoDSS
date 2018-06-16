.. _ruleset:

===================
Defining a rule set
===================

A rule set is built on two structures:

- A collection of name/value pairs
- An ordered list of values

Loading a rule set using a loader results in a Python dict, consisting of:

- dicts
- lists
- numbers
- strings

combined in any way you like. 

Actually this is all very well described on the `json website <https://www.json.org/>`_.

Of course, this description is very generic. A rule set has to be defined in a specific way to be useful for geoDSS.

A rule set contains of a heading and one or more rules. 

- The heading defines some properties of the rule set and some properties which are 'inherited' by the rules.
- The rules are the tests and processors against which teh subject will be evaluated.

Heading
-------

The heading contains the following example (in `yaml <http://yaml.org>`_ format)::


    name: test_bag_geocoder
    title: Test the BAG geocoder
    description: Test the BAG geocoder by geocoding an address and report the result
    logging:
        level: DEBUG
        file: "/home/marco/bag_geocoder_cgi.log"
    reporter: reporters.md
    reporter_args:
        output_format: html
        decision_false_report: "Uitkomst test: **negatief**"
        decision_error_report: "**Fout**: test kwam niet tot een beslissing of rapportage"
    settings:
        db:
            host: localhost
            port: 5432
            user: geoDSS
            password: geoDSS
            dbname: gisdefault
    rules:

Explanation (almost all arguments are optional):

- ``name``: a useful identifier meant for computers to read.
- ``title``: a useful identifier for humans to read. Most reporters will put this in the report. If left empty, then the ``name`` will be used as a title.
- ``description``: a description of this rule set. Most reporters will put this in the report.
- ``logging``: sets the logging properties:

  - ``level``:  Python log level. Usually one of: ``DEBUG``, ``INFO``, ``ERROR`` (defaults to ``INFO``)
  - ``format``: Python logging format string. Default: ``'%(asctime)s %(name)-12s %(levelname)-7s  %(message)s'``
  - ``file``:   A writeable file to write the log. This file will be log-rotated.

- ``reporter``: one of the reporter modules available in geoDSS. Refer to the `API documentation of the reporters <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/reporters/index.html>`_ for a full list and accepted arguments.
- ``reporter_args``: arguments to pass to the reporter. These are explained in the `API documentation of the reporters <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/reporters/index.html>`_.

    - ``output_format``: an argument accepted by the markdown reporter. This can be ``markdown`` or ``html``.
    - ``decision_false_report``: an argument accepted by the markdown reporter. This sets the string which will be reported when a test evaluates to `False`.
    - ``decision_error_report``: an argument accepted by the markdown reporter. This sets the string which will be reported when a test could not be evaluated due to an error.

- ``settings``: this provides a default for all rules. So each key under ``settings`` is added to the keys under the rules. If a rule has the same key defined then the definition in the rule is used.

    - ``db``: a key which servers as a default for the `tests.postgis_spatial_select <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/tests/postgis_spatial_select.m.html>`_ test.

- ``rules``: the rules as explained in the next section.

.. _rules:

Rules
-----

The rules are executed one by one in order. Rules are based either on :ref:`tests` or :ref:`processors`.

Of course, each test or processor needs its special configuration which is documented in the API documentation of `tests <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/tests/index.html>`_ and `processors <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/tests/processors.html>`_. 

Some settings are supported by all rules and processors. These are illustrated in the following example (in `yaml <http://yaml.org>`_ format)::

    rules:
    - a_unique_identifier_for_the_test:
        type: tests.request
        title: a title
        description: to explain something about the test
        report_template: "Report this string when the test evaluates to True"
        report: True
        break_on_error: True
    
Explanation:

- ``a_unique_identifier_for_the_test``: This serves as a unique identifier for the rule and must be unique within a rule set.
- ``type``: one of the :ref:`tests` or :ref:`processors` of geoDSS.
- ``title``: a human readable title for the rule. This will be reported by most reporters.
- ``description``: a description of the rule. This will be reported by most reporters.
- ``report_template``: The string to report when the test evaluates to True. Some processors are also able to report. This string is a template as most tests and reporters will replace a parameter like ``{this}`` by the value for this.
- ``report``: Optional, defaults to ``True``. If set to ``False`` the test or processor won't report. Useful for combining tests and report as one using the `tests.evaluate <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/tests/evaluate.m.html>`_ test. 
- ``break_on_error``: Optional, defaults to ``False``. geoDSS tries to execute all rules, even if one runs into an error. If ``break_on_error`` is set to ``True`` geoDSS will stop execution if the test or processor runs into an error.


