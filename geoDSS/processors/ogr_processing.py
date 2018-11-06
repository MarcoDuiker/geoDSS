# -*- coding: utf-8 -*-

from osgeo import ogr
from osgeo import gdal

try:
    import exceptions
except:
    pass

from ..processors.processor import processor
from ..processors.processor import utils

class ogr_processing(processor):
    '''
    This processor does basic ogr processing like Buffer or Area.
    Available functions are listed here: `https://gdal.org/python/osgeo.ogr.Geometry-class.html`.
    
    Dependencies
    ------------
    
    - osgeo

    Definition
    ----------

    `definition` is expected to be a dict having:

    `processor` (string):                 one of the ogr processing tools like Buffer, or Area. 
                                          You can use any function which operates on a geometry.
                                          These functions are listed on: `https://gdal.org/python/osgeo.ogr.Geometry-class.html`.

    `parameters` (list):                  the parameters which are taken by the processor;
                                          If a key available in the subject is specified, the value will be taken from that key.
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


    def execute(self, subject):
        ''' 
        Executes the processor.

        `subject` is expected to be a dict having:

        `geometry` (ewkt string):          a proper EWKT string representing the geometry of the subject
        '''

        gdal.UseExceptions()

        if not 'geometry' in subject:
            return self._handle_execution_exception(subject, 'Could not find key "geometry" in subject.')

        parameters = self.definition['parameters']
        for index, parameter in enumerate(parameters):
            if parameter in subject:
                parameters[index] = subject[parameter]

        ewkt = subject['geometry']
        try:
            g = ogr.CreateGeometryFromWkt(utils.wkt._get_WKT_geometry(ewkt))
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not create ogr geometry from subject: " + str(error))
        try:
            processor_to_call = getattr(g, self.definition['processor'])
        except Exception as error:
            return self._handle_execution_exception(subject, "ogr doesn't know the processor: " + self.definition['processor'])

        try:
            result = processor_to_call(*parameters)  # we might be more flexible using an eval(expression)
        except Exception as error:
            return self._handle_execution_exception(subject, "ogr error during processing: " + str(error))

        if result:
            self.executed = True
            if isinstance(result,ogr.Geometry):
                result = utils.wkt._EWKT_from_WKT(utils.wkt._get_SRID_string(ewkt),result.ExportToWkt())
            subject[self.definition['result_key']] = result
            
        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('{result}', str(result))
            self.result.append(result)

        return self._finish_execution(subject)
