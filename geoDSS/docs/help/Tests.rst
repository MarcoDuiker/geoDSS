.. _tests:

=====
Tests
=====

geoDSS has many tests which, together with the :ref:`processors`, provide the fundamental building blocks for a :ref:`rule set <ruleset>`.

A test will either evaluate to `True` or `False`. When the test evaluates to `True` something will be added to the report. A test optionally modifies the subject.

Tests are explained in detail in the `tests section of the API documentation <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/tests/index.html>`_

In this help, tests are explained at a more functional level. Don't forget to refer to the API documentation for all the relevant details.

unit_test
---------

The unit_test is only there to see if geoDSS is functioning properly. It won't test if other processors or tests function properly. It only tests the basic framework.

remark
------

The remark test always evaluates to `True`, so is designed to put a remark into the report.

To make this more useful, you can put in values from the subject by using the ``{parameter}`` syntax. Furthermore you can insert a timestamp by specifying ``{timestamp}`` in the report_template.

get_map
-------

The get_map test constructs a WMS GetMap request based on a geometry in the subject. Just like the `remark` test, this test always evaluates to `True`. So you can regard this test as something to put a map remark in the report.

You can add a buffer so that the geometry ends up in the middle of the map.

When using the html output of the standard markdown reporter a semi opaque red box indicating the middle of the image can be added.


key_value_compare
-----------------

This test compares a key from the subject with a value given in the rule or in the subject itself.

When comparing strings the ``==`` and ``in`` operators are most useful. This last one tests if the value is contained by the string.

When comparing numbers all operators are useful except for the ``in`` operator.


evaluate
--------

The evaluate test is designed to evaluate a combination of proviously executed tests using an expression. Eg.::

    rules.first_test and rules.second_test or rules.third_test

If such an expression evaluates to `True`, the report_template is reported. You can add a list of prveviously exectued tests from which to add the reports as well. This is most useful when these tests are configured with ``report: False`` to suppress reporting.

request
-------

This test does a http(s) request using GET, POST or HEAD. The test evaluates to `True` or `False` depending on the status code returned by the server or by testing if a string is present in the content.

URL and/ or data to send can be configured both in the rule as well as in the subject.

As a complete payload can be POSTed (via the subject), it is easy to test a WFS service with an extensive query.

If necessary, you can provide username and password for Basic Authetication or Digest Authentication. You can also add any header(s) you like to the request.

As geoDSS has a script to run in a scheduled manner, this test is well suited to create a monitor on a webservice. For this, it is nice that a timestamp, status_code, response_time and even te entire response can be inserted in the report_template via the ``{parameter}`` syntax.

The response from the server can also be added to the subject on any key you like.

postgis_spatial_select
----------------------

This test is the workhorse of geoDSS. You need to have access to PostgreSQL/ Postgis (either on localhost or another server).

This tests performs a query in the database and if one ore more rows are returned, the test evaluates to 'True'.

The query send to the database is in the following form::

    SELECT * FROM <schema>.<table> WHERE <relationship>(<relationship_parameters>) <where>

All ``<things written like this>`` are configured in the rule. In this way, most functions from the "Spatial Relationships and Measurements" section on the `PostGIS reference page <https://postgis.net/docs/reference.html>`_ can be used.

The test outputs one report for each line in the query results. In the report_template, the ``{column_name}`` syntax can be used to put the value in the column ``column_name`` in the report.

To use this test you need to set up a rule like (<where> is optional)::


    - dwithin_example:
        type: tests.postgis_spatial_select
        title: dwithin example with 1000 units (meters ?) distance
        description: ""
        schema: public
        table: your_table_name
        relationship: ST_DWithin
        parameters: 
        - "subject.geometry"
        - "wkb_geometry"
        - "1000"
        report_template: Found a hit with a value in the column your_column: {your_column}
        db:
            dbname: your_database_name

This rule is doing a Postgis ST_DWithin query. Under the "synopsis" section of the `documentation of ST_Dwithin <https://postgis.net/docs/ST_DWithin.html>`_ you can see that ST_Dwithin takes 3 parameters.
Exactly these parameters are defined in the ``parameters`` section of the example above.

- ``"subject.geometry"`` is substituted by the geometry in the subject (in the key ``geometry``).
- ``"wkb_geometry"`` is the name of the geometry column of the table
- ``1000`` is the distance in units of the spatial reference system the geometry column is in


wfs2_SpatialOperator
--------------------

This test sends a query to a WFS 2.0.0 service and if one or more rows are returned, the test evaluates to 'True'.

The test outputs one report for each line in the query results. In the report_template, the ``{column_name}`` syntax can be used to put the value in the column ``column_name`` in the report.

The most common WFS spatial operators are supported: 

    - Disjoint
    - DWithin
    - Intersects
    - Touches
    - Crosses
    - Within
    - Contains
    - Overlaps

To use this test you need to set up a rule like::

       - DWithin_example:
            type: tests.wfs_SpatialOperator
            title: Gemeenten binnen 40 km van de aanvraag
            description: ""
            url: https://geodata.nationaalgeoregister.nl/bestuurlijkegrenzen/wfs?
            typename: "bestuurlijkegrenzen:gemeenten"
            geometryname: geom
            namespace:
                prefix: app
                URI: "http://www.deegree.org/app"
            spatial_operator: DWithin
            distance: 40000
            report_template: Doorsturen naar B&W van gemeente {gemeentenaam}
