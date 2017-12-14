# -*- coding: utf-8 -*-
'''
The form generator generates a set of html form fields from a yaml definition.
An optional template can be passed, in which the the form fields will be embedded.

The form fields will be generated from the `form_fields` parameter in the yaml definition.

All other parameters in the yaml definition will be used for substitution in the template.

'''

import os

import yaml


def _getStringFromTemplate(template, subst, prefix='%', postfix='%'):
    '''
    Private method to replace all variables in the template named by prefix + key
    from the subst dictionary + postfix to the value from the subst dictionary.
    '''

    result = template
    for key, value in subst.items():
        result = result.replace(prefix + key + postfix, value)

    return result


def generate(form_yaml, template=None, prefix='%', postfix='%'):
    '''
    This method generates a set of form fields from a definition given in yaml-format.
    This is handy to automagically generate a html page for a user to enter a subject.

    To make things even easier a template can be supplied to add the form fields to a html page.
    Via parameter substitution parameters from the definition in yaml_format will be inserted
    into the template.

    In the form folder in the examples folder you'll find examples of both templates and form definition
    in yaml format to get you going. The template example is also handy to see an easy method to submit
    the form as a subject to a rule_set.

    Parameters
    ----------

    `form_yaml` (string) (required):        Either valid yaml or the path of a readable file containing yaml.

    `template` (string) (optional):         Either the template or the path of a readable file containing the template.
                                            The template must contain the substitable parameter 'generated_form_fields'
                                            which will be substituted by the generated form fields.

    `prefix`, `postfix` (string) (optional) Delimiters to specify a parameter in the template. Defaults to '%'.

    Definition
    ----------

    `form fields`                           The yaml definition is expected to contain at least a list of mappings named `form fields`.

    Each mapping contains the defintion of a form field. The following parameters are required in each mapping:

    - `name`                                The name of the field. This name is passed as the subject property name to the rule set.
    - `label`                               The label for this field to be shown to the user.
    - `type`                                The html form field type. Eg. `text`, `checkbox`, `radio`, `hidden`.

    Depending on the type extra parameters may be included:

    - `value`                               For text fields a default value. For a hidden field the value.
    - `values`                              For radio buttons you a list with key value pairs where the key is the label and
                                            the value is the value submitted when the user selects an option.

    Furthermore you can add arbitrary parameters to the definition. The values will be substituted into the template based on the name.


    Examples
    --------

    An example for a form definition yaml:

        title: geoDSS example form
        url: "http://localhost:8000/cgi-bin/interfaces.py"
        rule_set_file: "../geoDSS/examples/rule_sets/bag_geocoder_test.yaml"
        description: "By processing this form you'll etc etc ... "
        subtitle: "Subject"
        form_fields:
        - identificatie:
            name: identfificatie
            label: Identificatie
            type: text
        - huisnummer:
            name: huisnummer
            label: Huisnummer
            type: text
        - postcode:
            name: postcode
            label: Postcode
            type: text
        - brzo:
            name: brzo
            label: BRZO-bedrijf
            type: checkbox
        - prioriteit:
            name: prio
            label: Prioriteit
            type: radio
            values:
            - Laag: laag
            - Midden: midden
            - Hoog: hoog

    An example of a part of a template to illustrate parameter substitution:

        <h1>%title%</h1>
        <p class='geoDSS'><em class='geoDSS'>%description%</em></p>
        <h2>%subtitle%</h2>
        <form id='geoDSS' onsubmit="submit_form(this)">
            %generated_form_fields%
            <div class='button'>
                <input type="button" onClick="submit_form(this.parentNode.parentNode); return false;" value="Verwerk" ></input>
            </div>
        </form>

    The parameters indicated by the delimiter '%' will be subsituted from the definition.

    `%generated_form_fields%` will be substituted by the generated form fields.

    '''

    if os.path.exists(form_yaml):
        with open(form_yaml) as stream:
            y = yaml.load(stream)
    else:
        y = yaml.load(form_yaml)

    if os.path.exists(template):
        with open(template) as stream:
            template = stream.read()

    form = u''
    for field in y['form_fields']:
        fid = field.keys()[0]
        definition = field[fid]
        if 'values' in definition:
            form = form + '<p class="geoDSS label">%s</p>' % definition['label']
            values = definition['values']
        else:
            if 'value' in definition:
                values = [definition['value']]
            else:
                values = [""]
        for value in values:
            if type(value) == dict:
                label, value = value.items()[0]
            else:
                label = definition['label']
            field_id = fid + '_' + value
            form = form + '<p class="geoDSS">'
            form = form +   '<label class="geoDSS label" for="%s">%s </label>' % (field_id, label)
            form = form +   '<input class="geoDSS" id="%s" type="%s" name="%s" value="%s" ></input>' % (field_id, definition['type'], definition['name'], value)
            form = form + '</p>'

    if template:
        y.pop('form_fields')
        y['generated_form_fields'] = form
        return _getStringFromTemplate(template, y)
    else:
        return form
