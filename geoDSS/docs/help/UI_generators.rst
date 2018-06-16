=============
UI_generators
=============

UI-generators are meant to help creating a user interface for the end user.

Typically this involves generating a form where te user can specify the subject, and push a button to execute the subject against the rule_set.

Up till now geoDSS has only one UI_generator which generates a web form.

form
----

The form UI-generator generates a html form from a definition in `yaml <http://yaml.org/>`_ format.

The geoDSS script ``interfaces.py`` can be used to generate the form and serve it to the user. 

The following example generates a form to enter a string to use to search in Google search::
    
    title: geoDSS example form
    url: "http://localhost:8000/cgi-bin/interfaces.py"
    rule_set_file: "../geoDSS/examples/rule_sets/request.yaml"
    description: "Test google search by doing a search "
    subtitle: "Subject"
    form_fields:
    - search_string: 
        name: q
        label: Google search string
        value: "github+geoDSS"
        type: text

More information is in the `API documentation of the form generator <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/ui_generators/form.m.html>`_.