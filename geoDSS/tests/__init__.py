'''
Upon execution a tests evaluates a subject against a rule.

This evaluation results in a decision being either True or False.

When the decision is True the test reports according to the `report_template` given in the rule.

The report_template can be a simple string (Markdown formatted) or a string where parameters 
will be substituted with a value generated by the test. 
The documentation of the test should explains which parameters should be inserted how.

In the documentation of the tests is referred to a "definition". This is the rule as written in the rule_set.

In the documentation of the tests is referred to a "subject". A test will evaluate this subject against the rule. 
The test will ignore any paramters in this subject which is not needed for this particular test. 
So the examples given illustrate which parameters need to be included for the documented test. 
In real life more parameters will be present in a subject.

'''

from ..tests import evaluate, get_map, key_value_compare, postgis_spatial_select, remark, unit_test



