# -*- coding: utf-8 -*-

import random
import uuid

try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class random_point_geometry(processor):
    '''
    This processor creates a point geometry.
    
    Result
    ------
    
    Keys added to the subject on success:
    
    `geometry`:                           Point geometry.
    

    Definition
    ----------

    `definition` is expected to be a dict having:
    
     `format` (string)                  The expected format of the geometry. May be one of: `ewkt`, `gml3`, `gml2`.

     `srid` (string):                   The srid of the spatial reference system used.
     
     `bbox` (list):                     A list of 4 numbers [xmin, ymin, xmax, ymax] defining the bounding box within which the point will be generated.
     

     `report_template` (string):        (optional) String (with markdown support) to be reported on success.
                                        The following placeholders will be replaced
    
     - `{geometry}`                     The geometry generated.


    Rule example
    ------------

    a suitable yaml snippet would be:

        rules:
        - random_geometry:
            type: processors.random_point_geometry
            title: Random point geometry
            description: ""
            format: ewkt
            srid: 28992 
            bbox:
            - 125000
            - 350000
            - 250000
            - 550000
            report_template: "Generated the geometry: {geometry}"

    
    Subject example
    ---------------

    Any subject will do, so this one as well:

        subject = '{"postcode": "4171KG", "huisnummer": "74"}'
    '''


    def execute(self, subject):
        '''
        Executes the random point gemetry generator.

        `subject` can be any dict.
        
        Result
        ------
        
        Keys added to the subject on success:
    
        `geometry`:                        Point geometry.
        '''

        try:
            x = random.uniform(self.definition['bbox'][0], self.definition['bbox'][2])
            y = random.uniform(self.definition['bbox'][1], self.definition['bbox'][3])
        except Exception as error:
            return self._handle_execution_exception(subject, "Could generate random geometry point with error: `%s`" % str(error))
        
        if self.definition['format'] == 'ewkt':
            geometry = 'SRID=%s;POINT(%s %s)' % (self.definition['srid'], x, y)
        if self.definition['format'] == 'gml3':
            geometry = '''<gml:Point gml:id="%s" srsName="urn:ogc:def:crs:EPSG::%s"><gml:pos>%s %s</gml:pos></gml:Point>''' % (str(uuid.uuid4()), self.definition['srid'], x, y)
        if self.definition['format'] == 'gml2':
            geometry = '''<gml:Point gml:id="%s" srsName="urn:ogc:def:crs:EPSG::%s"><gml:coordinates>%s,%s</gml:coordinates></gml:Point>''' % (str(uuid.uuid4()), self.definition['srid'], x, y)
        subject['geometry'] = geometry
                        
        self.executed = True
        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('{geometry}', geometry)
            self.result.append(result)

        return self._finish_execution(subject)
