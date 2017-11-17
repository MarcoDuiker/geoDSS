# -*- coding: utf-8 -*-

import psycopg2
try:
    import exceptions
except:
    pass

from ..processors.processor import processor

# todo
# refactor met rebel ipv psycopg2:
# https://github.com/hugollm/rebel


class postgis_unit_test(processor):
    '''
    this processor provides a unit test for Postgis processing by buffering with distance 1

    definition is expected to be a dict having:
        db (dict):                          a dictionary specifying a postgis database connection

    a suitable yaml snippet would be:
        rules:
            postgis_unit_test:
                type: processors.postgis_unit_test
                title: processor unit test
                description: unit test by buffering subject geometry with distance 1
                db:
                    dbname: gisdefault

    a suitable subject would be:
        subject = {"geometry": "SRID=28992;POINT(125000 360000)"}
    '''

    def _get_postgis_connection(self,db):
        '''
        returns a postgis connection
        '''

        try:
            conn = psycopg2.connect(**db)
        except (Exception, psycopg2.DatabaseError) as error:
            return error

        return conn

    def execute(self, subject):
        '''
        executes the postgis unit test

        subject is expected to be a dicht having:
            geometry (ewkt string):              a proper EWKT string representing the geometry of the subject
        '''

        self.result = []

        conn = self._get_postgis_connection(self.definition['db'])
        if type(conn) == str:
            self.result = [conn]
            return

        cur = conn.cursor()
        try:
            cur.execute("SELECT ST_AsEWKT(ST_Buffer(ST_GeomFromEWKT(%s),1)) as geometry;", [subject['geometry']])
            if cur.rowcount == 0:
                raise exceptions.TypeError("Query returned zero rows.")
            if cur.rowcount > 1:
                raise exceptions.TypeError("Query returned multiple rows. Use an aggregation to force a result with one row.")
            else:
                row = cur.fetchone()
                subject['geometry'] = row[0]
        except (Exception, psycopg2.DatabaseError, exceptions.TypeError) as error:
            self.result.append(str(cur.query))
            self.result.append(str(error))
            return

        # for this unit test we will put the new subject in the report
        self.result.append("Modified subject to: " + str(subject))

        if cur:
            cur.close()
        if conn:
            conn.close()
        self.executed = True
        return subject      # as this is a processor return a modified subject
