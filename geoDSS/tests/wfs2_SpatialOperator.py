# -*- coding: utf-8 -*-

import os
import re
import requests
import shutil
import tempfile
import traceback

from osgeo import ogr, gdal

from owslib.fes import *
from owslib.etree import etree
from owslib.wfs import WebFeatureService

try:
    # python2
    from urllib import urlencode
except ImportError:
    # python3
    from urllib.parse import urlencode

try:
    import exceptions
except:
    pass
    
from ..tests.test import test
from ..tests.test import utils


class wfs2_SpatialOperator(test):
    '''
    This test constructs a WFS 2.0.0 SpatialOperator request.
    
    Dependencies
    ------------
    
    - osgeo
    - owslib
    
    Definition
    ----------

    `definition`                          is expected to be a dict having at least:

    `url` (string)                        service endpoint for the DWithin request
    
    `typenames` (list)                    a list of layers to be queried
    
    `geometryname` (string)               the name of the geometry field
    
    `namespace` (dict)                    a dict defining the namespace needed for a proper query. 
                                          Eg. `app="http://www.deegree.org/app"`
    
     - `prefix`                            the xml prefix used. eg. `app`
     
     - `URI`                               the xml namespace URI. eg. `"http://www.deegree.org/app"`
    
    `spatial_operator`                    the WFS Spatial Operator to use. Should be one of:
    
        - Disjoint
        - DWithin
        - Intersects
        - Touches
        - Crosses
        - Within
        - Contains
        - Overlaps

    `report_template` (string):           String to be reported when the test is True.
                                          If multiple rows are returned by the query, multiple reports will be written, but a report will not be duplicated.
                                          In the string columns in the result set of the query can be named.
                                          eg. `{my_param}` will be replaced by the value in the column my_param.


     Optionaly required:

     `distance` (number)                  The distance (buffer) around the subjects geometry (in meters) for the DWithin SpatialOperator
     
     
     Optionaly having:
     
     `srsName` (string)                   The name of the spatial reference system the WFS service should return the features in. eg. `EPSG:4326`. 
                                          If not given the service default spatial reference system wil be used.
                                          
     `headers` (dict)                     a dict defining the headers for the request. Of not given `'Content-Type': 'application/xml'` is used.
     
     `buffer` (number)                    a distance to buffer the subjects geometry with before sending it to the WFS server
     
     `single_request` (boolean)           Set to `true` (default) or `false`. When set to `true` al typenames will be send in a single request. 
                                          When set to `false` a separate request will be done for each typename


    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
            example:
                type: tests.wfs_SpatialOperator
                title: Gemeenten binnen 40 km van de aanvraag
                description: ""
                url: https://geodata.nationaalgeoregister.nl/bestuurlijkegrenzen/wfs?
                typenames: 
                - "bestuurlijkegrenzen:gemeenten"
                geometryname: geom
                namespace:
                    prefix: app
                    URI: "http://www.deegree.org/app"
                spatial_operator: DWithin
                distance: 40000
                report_template: Doorsturen naar B&W van gemeente {gemeentenaam}

    Subject Example
    ---------------

    a useful subject for this would be:

        subject = { "geometry": "SRID=28992;POINT(138034.181 452694.342)"}
    '''
       
        
    def _buffer(self, ewkt, distance):
        '''
        A private method which buffers the geometry with a distance
        '''
        
        g = ogr.CreateGeometryFromWkt(utils.wkt._get_WKT_geometry(ewkt))
        ng = g.Buffer(distance)

        return utils.wkt._EWKT_from_WKT(utils.wkt._get_SRID_string(ewkt),ng.ExportToWkt())

    def _getFeature(self):
        '''
        returns a xml wrapper for a getFeature request
        '''
        
        return '''<?xml version="1.0" encoding="UTF-8"?>
                        <GetFeature xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/2.0/wfs.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wfs/2.0" service="WFS" version="2.0.0">
                            %s
                        </GetFeature>'''
                        
    def _Query(self, namespace, typename, srsName = None):
        ''' 
        returns a xml wrapper for a Query
        '''
        
        if srsName:
            return ('''<Query xmlns:%s="%s" typeNames="%s" srsName="%s">''' % (namespace['prefix'],namespace['URI'],typename, srsName)) + "%s </Query>"
        else:        
            return ('''<Query xmlns:%s="%s" typeNames="%s">''' % (namespace['prefix'],namespace['URI'],typename)) + "%s </Query>"
     
    def _Filter(self):
        ''' 
        returns a xml wrapper for a Filter
        '''
        
        return '''<fes:Filter
                   xmlns:fes="http://www.opengis.net/fes/2.0"
                   xmlns:gml="http://www.opengis.net/gml/3.2"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.opengis.net/fes/2.0
                   http://schemas.opengis.net/filter/2.0/filterAll.xsd
                   http://www.opengis.net/gml/3.2
                   http://schemas.opengis.net/gml/3.2.1/gml.xsd">
                   %s
                </fes:Filter>'''
                
    def _SpatialOperator(self, spatial_operator, ewkt, geometryname, distance = None):
        ''' 
        Returns a SpatialOperator filter clause in xml.
        
        Does NOT support geometries of the MULTI type.
        
        spatial_operator should be one of:
        
        - Disjoint
        - DWithin
        - Intersects
        - Touches
        - Crosses
        - Within
        - Contains
        - Overlaps
        '''
        
        _supported_spatial_operators = ["Disjoint", "DWithin", "Intersects",
                                        "Touches", "Crosses", "Within",
                                        "Contains", "Overlaps"]
        if not spatial_operator in _supported_spatial_operators:
            self._handle_execution_exception(subject, "Spatial Operator %s not supported. Choose one of %s." % (spatial_operator, str(_supported_spatial_operators) ))

        _distance = ""
        if distance:
            _distance = '''<fes:Distance uom="m">%s</fes:Distance>''' % distance

        return '''<fes:%s>
                    <fes:ValueReference>%s</fes:ValueReference>
                    %s
                    %s
                </fes:%s>''' % (spatial_operator, geometryname, self._getGMLGeom(ewkt), _distance, spatial_operator)
                

                
    def execute(self, subject):
        ''' 
        Executes the test.

        `subject`       is expected a dict containing at least:
        
        - `geometry`    the geometry of the subject in EWKT. eg. `"SRID=28992;POINT(138034.181 452694.342)"`.
                        the MULTI variant of geometry types is not supported.
                     
        '''

        gdal.UseExceptions()

        _distance = None
        if 'distance' in self.definition:
            _distance = self.definition['distance']
            
        _srsName = None
        if 'srsName' in self.definition:
            _srsName = self.definition['srsName']
            
        _headers = {'Content-Type': 'application/xml'}
        if 'headers' in self.definition:
            _headers = self.definition['headers']
        
        _geometry = subject['geometry']
        if 'buffer' in self.definition:
            _geometry = self._buffer(subject['geometry'], self.definition['buffer'])
        #self.logger.debug('using geometry: ' + _geometry)
        
        _single_request = True
        if 'single_request' in self.definition:
            _single_request = self.definition['single_request'] 
            
        _type_names = self.definition['typenames']
        if _single_request:
            _type_names = [",".join(self.definition['typenames'])]
        
        tmp_folder = tempfile.mkdtemp()
        for _type_name in _type_names:
            _operator = self._SpatialOperator(self.definition['spatial_operator'], _geometry, self.definition['geometryname'], _distance)
            _filter = self._Filter() % _operator
            _query = self._Query(self.definition['namespace'], _type_name, _srsName) % _filter
            payload = self._getFeature() % _query

            self.logger.debug("Sending WFS-query to: " + self.definition['url'])
            self.logger.debug(payload)
            try:
                r = requests.post(url = self.definition['url'], data=payload, headers=_headers)
            except Exception as error:
                self.logger.debug(traceback.format_exc())
                return self._handle_execution_exception( subject, 'Failed WFS request with error: ' + str(error) )
                
            if r.status_code == requests.codes.ok:
                if "<Exception" in r.content or ":Exception" in r.content:
                    self.logger.debug("Found Exception in WFS response:" + r.content)
                    return self._handle_execution_exception( subject, 'Failed WFS request with error: ' + r.content )
                gml_file = os.path.join(tmp_folder,"response.gml")
                with open(gml_file, 'wb') as f:
                    f.write(r.content)

                dataSource = ogr.Open(gml_file)
                if dataSource is None:
                    return self._handle_execution_exception( subject, 'Failed reading WFS request for an unknown reason')
                else:
                    self.decision = False
                    layer = dataSource.GetLayer()
                    if layer:
                        layerDefinition = layer.GetLayerDefn()
                                        
                        cols = []
                        for i in range(layerDefinition.GetFieldCount()):
                            cols.append(layerDefinition.GetFieldDefn(i).GetName())

                        for feature in layer:
                            to_report = self.definition['report_template']
                            self.decision = True
                            for col in cols:
                                if "{%s}" % col in to_report:
                                    to_report = to_report.replace("{%s}" % col, str(feature.GetField(col)))
                            if not to_report in self.result:
                                self.result.append(to_report)
                        
            else:
                return self._handle_execution_exception( subject, 'WFS returned statuscode: ' + str(r.status_code) )
                
        shutil.rmtree(tmp_folder)

        self.executed = True                                                            # don't forget to set self.executed to True, 
                                                                                        # otherwise "Error: test is not executed:" will be added to the report as well

        return self._finish_execution(subject)                                          # Returns False to end execution or the subject to continue to the next test 
