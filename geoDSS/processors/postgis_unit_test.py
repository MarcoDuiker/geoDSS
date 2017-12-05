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
    this processor provides a unit-like test for Postgis processing by buffering with distance 1

    Definition
    ----------

    `definition` is expected to be a dict having:

    `db` (dict):                          a dictionary specifying a postgis database connection

    Rule example
    ------------

    a suitable yaml snippet would be:

        rules:
            my_postgis_test:
                type: processors.postgis_unit_test
                title: processor unit test
                description: unit-like test by buffering subject geometry with distance 1
                db:
                    dbname: gisdefault

    Subject example
    ---------------

    a usefull subject for this would be:

        subject = {"geometry": "SRID=28992;POINT(125000 360000)"}

    '''

    def _get_postgis_connection(self,db):
        '''
        Private method; returns a postgis connection.
        '''

        try:
            conn = psycopg2.connect(**db)
        except (Exception, psycopg2.DatabaseError) as error:
            return error

        return conn

    def execute(self, subject):
        '''
        Executes the postgis unit-like test processor

        `subject` is expected to be a dict having:

        `geometry` (ewkt string):          a proper EWKT string representing the geometry of the subject
        '''

        self.result = []

        conn = self._get_postgis_connection(self.definition['db'])
        if type(conn) == str:
            return self._handle_execution_exception(subject, "Could not get database connection with error: " + str(conn))

        cur = conn.cursor()

        if not 'geometry' in subject:
            return self._handle_execution_exception(subject, 'Could not find key "geometry" in subject.')

        try:
            cur.execute("SELECT ST_AsEWKT(ST_Buffer(ST_GeomFromEWKT(%s),1)) as geometry;", [subject['geometry']])
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

        self.result.append("Modified subject to: " + str(subject))

        if cur:
            cur.close()
        if conn:
            conn.close()
        self.executed = True

        return self._finish_execution(subject)

