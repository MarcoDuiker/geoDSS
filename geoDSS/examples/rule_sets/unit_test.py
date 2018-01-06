{"name": "set 1",
 "title": "Rule set doing the unit test",
 "description": "use the unit test to test the framework",
 "rules": [
    {"unit_test": {
        "type": "tests.unit_test",
        "title": "unit test",
        "description": "unit test testing",
        "report_template": "Action should be taken"}
    },{
        "postgis_unit_test": {
            "type": "processors.postgis_unit_test",
            "title": "processor unit test",
            "description": "unit test by buffering subject geometry with distance 1",
            "db":
                {"dbname": "gisdefault"}
        }
    }
 ]
}
