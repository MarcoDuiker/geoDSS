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

    definition is expected to be a dict having:
        db (dict):                          a dictionary specifying a postgis database connection
        schema (string):                    schema name
        table (string):                     table name
        relationship (string):              one of the postgis spatial relationships as ST_Contains, ST_DWithin, etc 
        parameters (list):                  the parameters which are taken by the relationship;
                                            "subject.geometry" will be replaced by the subjects geometry
        report_template (format string):    Python format-like string to be reported when test is True
                                            in the format-like string columns in the result set of the query can be named
                                            eg. {my_param} will be replaced by the value in the column my_param
    optionally:
        where (string):                     an aditionaly clause to attach to the WHERE clause. should start with a boolean operator like AND, OR, XOR

    '''

    def execute(self, subject):
        ''' 
        Executes the test.

        subject is expected to be a dict having:
            geometry (ewkt string):          a proper EWKT string representing the geometry of the subject
        optionally:
            params (dict):                   a dict containing key value pairs to be inserted in the optional WHERE clause given in the definition of the rule
        '''

        self.decision = False
        self.result = []
        self.executed = False

        if "subject.geometry" in self.definition['parameters']:
            loc = self.definition['parameters'].index("subject.geometry")
            self.definition['parameters'][loc] = "ST_GeomFromEWKT('%s')" % subject['geometry']

        where = ' %s(%s) ' % (self.definition['relationship'], ','.join(self.definition['parameters']))
        if 'where' in self.definition.keys():
            if subject['params']:
                where = where + self.definition['where'].format(subject['parameters'])
            else:
                where = where + self.definition['where']

        try:
            conn = psycopg2.connect(**self.definition['db'])
            cur = conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            self.result = [str(error)]
            return

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
                    self.result.append(to_report)
        except (Exception, psycopg2.DatabaseError) as error:
            self.result = [str(error)]
            return

        if cur:
            cur.close()
        if conn:
            conn.close()
        self.executed = True

        return True                    # Returning False will end execution


