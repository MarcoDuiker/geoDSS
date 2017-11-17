# -*- coding: utf-8 -*-

import psycopg2
try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class postgis_processing(processor):
    '''
    this processor does basic Postgis processing like ST_Buffer or ST_Transform

    definition is expected to be a dict having:
        db (dict):                          a dictionary specifying a postgis database connection
        processor (string):                 one of the postgis spatial processing as ST_Buffer, ST_Transform, etc 
        parameters (list):                  the parameters which are taken by the processor;
                                            "subject.geometry" will be replaced by the subjects geometry
    '''

    def execute(self, subject):
        ''' 
        Executes the processing.

        subject is expected to be a dict having:
            geometry (ewkt string):          a proper EWKT string representing the geometry of the subject
        '''

        self.result = []

        if "subject.geometry" in self.definition['parameters']:
            loc = self.definition['parameters'].index("subject.geometry")
            self.definition['parameters'][loc] = "ST_GeomFromEWKT('%s')" % subject['geometry']

        try:
            conn = psycopg2.connect(**self.definition['db'])
            cur = conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            self.result = [str(error)]
            return

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
            self.result.append(str(error))
            return

        if cur:
            cur.close()
        if conn:
            conn.close()
        self.executed = True
        return subject      # as this is a processor return a modified subject
