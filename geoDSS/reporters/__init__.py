'''
The reporters module provides reporters for the rule_set and rules.

The standard reporter is reporters.md, providing a markdown reporter. This one can output html as well.

Extending the reporters.md reporter or creating a new one can easily be done with pandoc.

Of course, you can also convert via https://www.docverter.com/

When extending mind the following:

- rules report via a list of strings. These strings can be added to the rport with something like:
        for result in rule.result:
            markdown = markdown + result + '\n'
- a subject is a dictionary containing lists, dictionaries, strings and numbers. Adding these to the report requires some pretty printing.

'''

from ..reporters import md, plain_text
