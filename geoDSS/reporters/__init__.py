'''
The reporters module provides reporters for the rule_set and rules.

The standard reporter is md, providing a markdown reporter. This one can output html as well.

Extending the md reporter or creating a new one can easily be done with pandoc.

Of course, you can also convert via https://www.docverter.com/
'''

from ..reporters import md
