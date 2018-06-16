.. _report:

=========
Reporters
=========

The reporters report whatever the rules ask them to report.

geoDSS has serveral reporters. In the rule_set you define the reporter to use. 

If no reporter is specified the default markdown reporter will be used.

md
--

md is the markdown reporter which is the default reporter and will report in markdown or html.

The report will contain a heading with information about the rule_set and the subject followed by the reports of the rules.

The reporter can be configured in the rule_set file as illustrated in the following example::

    reporter: reporters.md
    reporter_args:
      output_format: html
      decision_false_report: "Uitkomst test: **negatief**"
      decision_error_report: "**Fout**: test kwam niet tot een beslissing of rapportage"

More information can be found in the `API documentation of the md reporter <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/reporters/md.m.html>`_.

plain_text
----------

The plain_text reporter reports in plain text and is especially useful for generating .csv files.

For this the header of the .csv file is put in the description item of the rule_set. 

Each rule will add a line to the .csv file. Make sure that the output of the rule matches the header.

This is illustrated in the following example of a rule set::

    # With this rule set we can generate a CSV file by batch geocoding subjects
    name: batch_geocoder
    title: Batch geocode using the PDOK Locatieserver geocoder
    # using the plain_text reporter we can use the description to generate the header 
    description: wkt_geom,address,x,y
    reporter: reporters.plain_text
    logging:
      level: DEBUG
      file: "/home/marco/batch_geocoder.log"
    rules:
    - batch:
        type: processors.pdok_locatieserver
        title: geocoder
        description: ""
        url: "https://geodata.nationaalgeoregister.nl/locatieserver/v3/free?q="
    # the report template should match the header we created using the description
        report_template: '{wkt_geometry},"{address}",{x},{y}'

More information can be found in the `API documentation of the plain_text reporter <https://marcoduiker.github.io/geoDSS/geoDSS/docs/API/reporters/plain_text.m.html>`_.