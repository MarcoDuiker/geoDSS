# -*- coding: utf-8 -*-

from osgeo import ogr
from osgeo import gdal

try:
    import exceptions
except:
    pass

from ..processors.processor import processor

class ogr_processing(processor):
    '''
    This processor does basic ogr processing like Buffer or Area.
    
    Dependencies
    ------------
    
    - osgeo

    Definition
    ----------

    `definition` is expected to be a dict having:

    `processor` (string):                 one of the ogr processing tools like Buffer, or Area 

    `parameters` (list):                  the parameters which are taken by the relationship;
                                          The processor always works on the subjects geometry.

    `result_key` (string):                The name of the key to store the result.
                                          If the key exists, the existing value will be overwritten.
                                          Otherwise a new key will be added.

     `report_template` (string):        (optional) String (with markdown support) to be reported on success.

                                        The following placeholders will be replaced:
    
     - `{result}`                       The resulting value from the proces.


    Subject example
    ---------------

    a usefull subject for this would be:

        subject = { "geometry": "SRID=28992;POINT(138034.181 452694.342)"}

    '''

    def _get_srsName(self, ewkt):
        '''
        A private method to get a proper srsName for the WFS request from an EWKT string
        '''

        code = ewkt.split(';')[0].split('=')[1].strip()
        return "urn:ogc:def:crs:EPSG::%s" % str(code)
        
    def _get_SRID_string(self,ewkt):
        '''
        A private method to get the EWKT projection string from an EWKT string
        '''
        
        return ewkt.split(';')[0].strip()
        
    def _get_WKT_geometry(self, ewkt):
        '''
        A private method to get a WKT geometry string from an EWKT string
        '''
        
        return ewkt.split(';')[1].strip()
        
    def _EWKT_from_WKT(self, srid, wkt ):
        '''
        Private method to get a valid EWKT geometry string from a WKT string and a EWKT SRID string
        '''
        
        return ';'.join([srid,wkt])

    def execute(self, subject):
        ''' 
        Executes the processor.

        `subject` is expected to be a dict having:

        `geometry` (ewkt string):          a proper EWKT string representing the geometry of the subject
        '''

        gdal.UseExceptions()

        if not 'geometry' in subject:
            return self._handle_execution_exception(subject, 'Could not find key "geometry" in subject.')

        ewkt = subject['geometry']
        try:
            g = ogr.CreateGeometryFromWkt(self._get_WKT_geometry(ewkt))
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not create ogr geometry from subject: " + str(error))
        try:
            processor_to_call = getattr(g, self.definition['processor'])
        except Exception as error:
            return self._handle_execution_exception(subject, "ogr doesn't know the processor: " + self.definition['processor'])

        try:
            result = processor_to_call(*self.definition['parameters'])
        except Exception as error:
            return self._handle_execution_exception(subject, "ogr error during processing: " + str(error))

        if result:
            self.executed = True
            if isinstance(geom,ogr.Geometry):
                result = self._get_SRID_string(self,ewkt) + ";" + result.ExportToWkt()
            subject[self.definition['result_key']] = result
            
        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('{result}', str(result))
            self.result.append(result)

        return self._finish_execution(subject)
