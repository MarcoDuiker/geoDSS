# -*- coding: utf-8 -*-

import psycopg2
try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class postgis_processing(processor):
    '''
    This processor does basic Postgis processing like ST_Buffer or ST_Transform.

    Definition
    ----------

    `definition` is expected to be a dict having:

    `db` (dict):                          a dictionary specifying a postgis database connection

    `processor` (string):                 one of the postgis spatial processing as ST_Buffer, ST_Transform, etc 

    `parameters` (list):                  the parameters which are taken by the relationship;
                                            "subject.geometry" will be replaced by the subjects geometry


    Subject example
    ---------------

    a usefull subject for this would be:

        subject = { "geometry": "SRID=28992;POINT(138034.181 452694.342)"}

    '''

    def execute(self, subject):
        ''' 
        Executes the processor.

        `subject` is expected to be a dict having:

        `geometry` (ewkt string):          a proper EWKT string representing the geometry of the subject
        '''

        if "subject.geometry" in self.definition['parameters']:
            loc = self.definition['parameters'].index("subject.geometry")
            if 'geometry' in subject:
                self.definition['parameters'][loc] = "ST_GeomFromEWKT('%s')" % subject['geometry']
            else:
                return self._handle_execution_exception(subject, 'Could not find key "geometry" in subject.')

        try:
            conn = psycopg2.connect(**self.definition['db'])
            cur = conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            return self._handle_execution_exception(subject, "Could not get database connection with error: " + str(error))

        try:
            cur.execute("SELECT ST_AsEWKT(%s(%s)) as geometry;", (self.definition['processor'], ','.join(self.definition['parameters'])) )
            self.logger.debug("Executed query: " + cur.query)
            if cur.rowcount == 0:
                raise exceptions.TypeError("Query returned zero rows.")
            if cur.rowcount > 1:
                raise exceptions.TypeError("Query returned multiple rows. Use an aggregation to force a result with one row.")
            else:
                row = cur.fetchone()
                subject['geometry'] = row[0]
        except (Exception, psycopg2.DatabaseError, exceptions.TypeError) as error:
            return self._handle_execution_exception(subject, "SQL query %s returned error %s" % (str(cur.query), str(error)))

        if cur:
            cur.close()
        if conn:
            conn.close()
        self.executed = True

        return self._finish_execution(subject)
