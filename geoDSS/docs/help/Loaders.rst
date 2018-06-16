=======
Loaders
=======

A loader loads a rule_set file. 

geoDSS comes with several loaders. As loaders are very easy to create, it is likely that more loaders will follow. 

Of course, you can write your own loader as well.

In the end, a rule_set is nothing more than a Python dict, consisting of:

- dicts
- lists
- numbers
- strings

combined in any way you like. 

Actually this is very well described on the `json website <https://www.json.org/>`_::
    
    JSON is built on two structures:

    A collection of name/value pairs. In various languages, this is realized as an object, record, struct, dictionary, hash table, keyed list, or associative array.
    An ordered list of values. In most languages, this is realized as an array, vector, list, or sequence.

    These are universal data structures. Virtually all modern programming languages support them in one form or another. It makes sense that a data format that is interchangeable with programming languages also be based on these structures.



In the examples folder of geoDSS you'll find an example file for each loader.

Loaders (and rule_sets) are explained in more detail in the `loaders section of the API documentation <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/loaders/index.html>`_.

yaml_loader
-----------

Loads a rule set from a `yaml <http://yaml.org/>`_ file.

json_loader
-----------

Loads a rule set from a `json <https://www.json.org/>`_ file.


python_loader
-------------

Loads a rule set from a python file.
