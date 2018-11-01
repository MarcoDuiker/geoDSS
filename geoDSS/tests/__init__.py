'''
Upon execution of a rule set, a subject is evaluated by each rule in order.

When the rule is based on a test, this evaluation results in a decision being either True or False.

When the decision is True the test reports according to the `report_template` given in the rule.

The report_template can be a simple string or a string where parameters 
will be substituted with a value generated by the test. 
The documentation of the test should explain which parameters should be inserted how.

Using the standard Markdown reporter the strings reported support Markdown. Other reporters might support something different. 
Documentation of the reporter should clarify that.

In the documentation of each test is referred to a "definition". This is the rule as written in the rule_set.

In the documentation of each test is referred to a "subject". A test will evaluate this subject against the rule. 
The test will ignore any parameters in this subject which is not needed for this particular test. 
So the examples given illustrate which parameters need to be included for the documented test. 
In real life more parameters will be present in a subject.

'''

# first import all tests dependent on python libraries needed by geoDSS only.
from ..tests import evaluate, \
                    get_map, \
                    key_value_compare, \
                    remark, \
                    request, \
                    unit_test

# then try to import other tests as well; skip a test if import fails.
try:
    from ..tests import postgis_spatial_select
except:
    pass

try:
    from ..tests import rss
except:
    pass

try:
    from ..tests import wfs2_SpatialOperator
except:
    pass
    
# and as long as we are developing we try the import here to prevent exceptions being caught.
from ..tests import pdf
