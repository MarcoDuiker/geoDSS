.. _subject:

==================
Defining a subject
==================

A subject is built on two structures:

- A collection of name/value pairs
- An ordered list of values

The subject is passed to the rules in the rule set as a Python dict, consisting of:

- dicts
- lists
- numbers
- strings

combined in any way you like. 

Of course, this description is very generic. A subject has to fit the rules defined in the rule set where it is evaluated against. For example a processor which geocodes an address needs an address in the subject.

Most :ref:`tests` and :ref:`processors` expect the subject to be a simple list of key-value pairs like these examples (in `json <https://json.org>`_ format):

tests.get_map:: 

    {"geometry": "SRID=28992;POINT(136905.198 430762.454)"}

processors.pdok_locatieserver::

    {"postcode": "4171KG", "huisnummer": "74"}

tests.request::
    
    {"q": "github+geoDSS"}
