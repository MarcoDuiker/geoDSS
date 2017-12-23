'''
Upon execution a tests evaluates a subject against a rule..

When the rule is based on a processor, the processor returns modified subject. 
Optionally processor reports according to the `report_template` given in the rule.

The report_template can be a simple string or a string where parameters 
will be substituted with a value generated by the test. 
The documentation of the test should explains which parameters should be inserted how.

Using the standard Markdown reporter the strings reported support Markdown. Other reporters might support something different. 
Documentation of the reporter should clarify that.

In the documentation of the processorss is referred to a "definition". This is the rule as written in the rule_set.

In the documentation of the processorss is referred to a "subject". A processors will modify this subject according to the rule. 
The processor will ignore any parameters in this subject which is not needed for this particular processor. 
So the examples given illustrate which parameters need to be included for the documented processor. 
In real life more parameters will be present in a subject.

'''

from ..processors import bag_geocoder, pdok_locatieserver, postgis_processing, postgis_unit_test, random_point_geometry, random_value
