'''
The loaders module is a provider for rule_set loaders.

The default loader is yaml_loader which loads a rule_set from a yaml file.

A rule set is a simple object with some generic properties and some rules. 

Definition
----------

`definition` is expected to be a dict having generic properties and a list of rules.

The generic properties of a rule set contain at least the following:

- `name` (string)                   A name for the rule set.
- `title` (string)                  A title for the rule set. If not given in the defintion,
                                    the name is used as a title as well.
- `description` (string)            A description of the rule set. If not given, it is set
                                    to an empty string.
- `logging` (dict)                  A defintion for a logger. If not given a default logger is used.
  - `level`                             Python log level. Usually one of: DEBUG, INFO, ERROR (defaults to INFO)
  - `format`                            Python logging format string. Default: '%(asctime)s %(name)-12s %(levelname)-7s  %(message)s'
  - `file`                              A writeable file to write the log. This file will be log-rotated.
- `reporter` (string)               The reporter module to be used. If not given, the reporters.md
                                    markdown reporter is used.
- `reporter_args` (dict)            Arguments to pass to the reporter. Which are accepted you'll find in the API docs of the reporter.
                                    The default markdown reporter accepts the following optional parameters:
  - `output_format` (string)            `markdown` or `html`. Defaults to `markdown`.
  - `decision_false_report` (string)    The string to report when a test is evaluates to False.
  - `decision_error_report` (string)    The string to report when a test did not evaluate but encounterd an error.
                            
Optionally the generic properties can contain:

- `settings` (dict)                 A settings object passed to all the rule. Al properties defined
                                    in the settings are available as if they were defined in the rule.
                                    If a property of `settings` is defined in a rule, then that 
                                    property is used, and not the property of this settings object.

                          
The rule set contains a list of rules. The properties of these rules depend on the processors and tests
used. Please refer to the docs of those.

The definition of a rule is a dict having at least the following properties:

- `name`  (string)                  A name for the rule. 
- `title`  (string)                 A title for the rule. If not given in the defintion,
                                    the name is used as a title as well.
- `description` (string)            A description of the rule set. Do not leave empty.
                                    An empty string (`""`) is allowed.
                            
The defintion of a test can contain at least the following properties:

- `report_template` (string)        The string which will be reported when the test evaluates to True.
                                    Most tests will support some form of parameter substitution to allow
                                    more detailed reporting on the test result. Please refer to the documentation
                                    of the tests for more info on this.
                            
The defintion of rules can have the following optional properties:

- `break_on_error` (bool)           Defaults to `False`. If set `True`, and the test or processor does not return a result at all,
                                    the processing will stop after this rule. When set to `False` geoDSS tries to continue after
                                    errors.
- `report` (bool)                   Defaults to `True`. If set to `False`, the rule will not report when the test evaluates to True.

Example
-------

A Rule set example in yaml format (more examples can be found in the examples folder):

    # a collection of different rules
    name: various_rules_test
    title: Doing some different tests
    description: ""
    logging:
      level: DEBUG
      file: "/home/marco/bag_geocoder_cgi.log"
    settings:
        db:
            dbname: gisdefault
    rules:
    - remark:
        type: tests.remark
        title: Be aware!
        description: ""
        report_template: don't forget a description cannot be empty; use quotes if you don't want a description
    - select_gemeente:
        type: tests.postgis_spatial_select
        title: Gemeenten binnen 40 km van de aanvraag
        description: ""
        schema: public
        table: gem_2009_gen
        relationship: ST_DWithin
        parameters: 
        - "subject.geometry"
        - "wkb_geometry"
        - "40000"
        report_template: Doorsturen naar B&W van gemeente {gm_naam}

'''

from ..loaders import json_loader, yaml_loader, python_loader
