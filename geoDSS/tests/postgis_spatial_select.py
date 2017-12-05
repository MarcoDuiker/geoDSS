# -*- coding: utf-8 -*-

import psycopg2
try:
    import exceptions
except:
    pass

from ..tests.test import test


class postgis_spatial_select(test):
    '''
    This test performs a basic postgis select test.

    Definition
    ----------

    `definition` is expected to be a dict having:

    `db` (dict):                          a dictionary specifying a postgis database connection

    `schema` (string):                    schema name

    `table` (string):                     table name

    `relationship` (string):              one of the postgis spatial relationships as ST_Contains, ST_DWithin, etc 

    `parameters` (list):                  the parameters which are taken by the relationship;
                                            "subject.geometry" will be replaced by the subjects geometry

    `report_template` (string):           String to be reported when the test is True.
                                          If multiple rows are returned by the query, multiple reports will be written, but a report will not be duplicated.
                                          In the string columns in the result set of the query can be named.
                                          eg. `{my_param}` will be replaced by the value in the column my_param.
    
    optionally having:

    `where` (string):                     an aditionaly clause to attach to the WHERE clause. Should start with a boolean operator like AND, OR, XOR.

    Rule example
    ------------

    a useful yaml snippet for this test would be:

        - select_gemeente:
            type: tests.postgis_spatial_select
            title: Gemeenten binnen 40 km van de aanvraag
            description: ""
            schema: public
            table: gem_2009_gen
            relationship: ST_DWithin
            parameters: 
            - "subject.geometry"
            - "wkb_geometry"
            - "40000"
            report_template: Doorsturen naar B&W van gemeente {gm_naam}
            db:
                dbname: gisdefault

    Subject example
    ---------------

    a usefull subject for this would be:

        subject = { "geometry": "SRID=28992;POINT(138034.181 452694.342)"}

    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        `subject` is expected to be a dict having:

        `geometry` (ewkt string):          a proper EWKT string representing the geometry of the subject
        
        optionally having:
            
        `params` (dict):                   a dict containing key value pairs to be inserted in the optional WHERE clause given in the definition of the rule
        '''

        if "subject.geometry" in self.definition['parameters']:
            loc = self.definition['parameters'].index("subject.geometry")
            if 'geometry' in subject:
                self.definition['parameters'][loc] = "ST_GeomFromEWKT('%s')" % subject['geometry']
            else:
                return self._handle_execution_exception(subject, 'Could not find key "geometry" in subject.')

        try:
            where = ' %s(%s) ' % (self.definition['relationship'], ','.join(self.definition['parameters']))
            if 'where' in self.definition.keys():
                if subject['params']:
                    where = where + self.definition['where'].format(subject['parameters'])
                else:
                    where = where + self.definition['where']
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not construct the SQL WHERE clause with error: " + str(error))

        try:
            conn = psycopg2.connect(**self.definition['db'])
            cur = conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            return self._handle_execution_exception(subject, "Could not get database connection with error: " + str(error))

        try:
            sql_string = 'SELECT * FROM %s.%s WHERE %s ;' % (self.definition['schema'], self.definition['table'], where)
            self.logger.debug("Executing query: " + sql_string)
            cur.execute(sql_string)
            cols = [desc[0] for desc in cur.description]
            
            if cur.rowcount == 0:
                self.decision = False
            else:
                self.decision = True
                rows = cur.fetchall()
                for row in rows:
                    to_report = self.definition['report_template']
                    for col in cols:
                        if "{%s}" % col in to_report:
                            to_report = to_report.replace("{%s}" % col, str(row[cols.index(col)]))
                    if not to_report in self.result:
                        self.result.append(to_report)
        except (Exception, psycopg2.DatabaseError) as error:
            return self._handle_execution_exception(subject, "SQL query %s returned error %s" % (str(cur.query), str(error)))

        if cur:
            cur.close()
        if conn:
            conn.close()
        self.executed = True

        return self._finish_execution(subject)


