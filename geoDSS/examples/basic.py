import geoDSS                                                           # be sure this is possible by installing geoDSS 
                                                                        # or invoking this from the right working dir

r = geoDSS.rules_set('geoDSS/examples/rule_sets/unit_test.yaml')        # and then check this path as well
r.execute( subject = {  'result': True,
                        'geometry': 'SRID=28992;POINT(125000 360000)'
                     })
r.report()
print(r)
