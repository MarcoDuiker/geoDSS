# -*- coding: utf-8 -*-

import os
import re
import requests
import shutil
import tempfile
import traceback

try:
    from osgeo import ogr, gdal
except:
    pass

try:
    from owslib.fes import *
    from owslib.etree import etree
    from owslib.wfs import WebFeatureService
except:
    pass

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

class wfs2_SpatialOperator(test):
    '''
    This test constructs a WFS 2.0.0 SpatialOperat0r request.
    
    Definition
    ----------

    `definition`                          is expected to be a dict having at least:

    `url`                                 service endpoint for the DWithin request
    
    `typename`                            the name of the layer queried
    
    `geometryname`                        the name of the geometry field
    
    `namespace`                           a dict defining the namespace needed for a proper query. Eg. `app="http://www.deegree.org/app"`
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

     `distance`                            the distance (buffer) around the subjects geometry (in meters) for the DWithin SpatialOperator


    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
            example:
                type: tests.wfs_SpatialOperator
                title: Gemeenten binnen 40 km van de aanvraag
                description: ""
                url: https://geodata.nationaalgeoregister.nl/bestuurlijkegrenzen/wfs?
                typename: "bestuurlijkegrenzen:gemeenten"
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

    class _WKTParser:
        """ 
        Private class to grab gml posList and geoType from WKT.

        Modified from pysal which is Modified from... 

        - URL: http://dev.openlayers.org/releases/OpenLayers-2.7/lib/OpenLayers/Format/WKT.js
        - Reg Ex Strings copied from OpenLayers.Format.WKT
        """

        regExes = {'typeStr': re.compile('^\s*([\w\s]+)\s*\(\s*(.*)\s*\)\s*$'),
                   'spaces': re.compile('\s+'),
                   'parenComma': re.compile('\)\s*,\s*\('),
                   'doubleParenComma': re.compile('\)\s*\)\s*,\s*\(\s*\('),  # can't use {2} here
                   'trimParens': re.compile('^\s*\(?(.*?)\)?\s*$')}

        def __init__(self):
            self.parsers = p = {}
            p['point'] = self.Point
            p['linestring'] = self.LineString
            p['polygon'] = self.Polygon

        def Point(self, geoStr):
            return [geoStr.strip()]

        def LineString(self, geoStr):
            return geoStr.strip().split(',')

        def Polygon(self, geoStr, outer_ring_only = True):
            rings = self.regExes['parenComma'].split(geoStr.strip())
            for i, ring in enumerate(rings):
                ring = self.regExes['trimParens'].match(ring).groups()[0]
                ring = self.LineString(ring)
                rings[i] = ring
                if outer_ring_only:
                    return rings[0]
            return rings
            
        def fromWKT(self, wkt, returnGeoType = False):
            matches = self.regExes['typeStr'].match(wkt)
            if matches:
                geoType, geoStr = matches.groups()
                geoType = geoType.lower().strip()
                try:
                    if returnGeoType:
                        return geoType, self.parsers[geoType](geoStr)
                    else:
                        return self.parsers[geoType](geoStr)
                except KeyError:
                    raise NotImplementedError("Unsupported WKT Type: %s" % geoType)
            else:
                return None
        
        __call__ = fromWKT

    def _get_srsName(self, ewkt):
        '''
        A private method to get a proper srsName for the WFS request
        '''

        code = ewkt.split(';')[0].split('=')[1].strip()
        return "urn:ogc:def:crs:EPSG::%s" % str(code)
        
    def _getFeature(self):
        '''
        returns a xml wrapper for a getFeature request
        '''
        
        return '''<?xml version="1.0" encoding="UTF-8"?>
                        <GetFeature xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/2.0/wfs.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wfs/2.0" service="WFS" version="2.0.0">
                            %s
                        </GetFeature>'''
                        
    def _Query(self, namespace, typename):
        ''' 
        returns a xml wrapper for a Query
        '''
        
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

        if distance:
            distance = '''<fes:Distance uom="m">%s</fes:Distance>''' % distance
            
        return '''<fes:%s>
                    <fes:ValueReference>%s</fes:ValueReference>
                    %s
                    %s
                </fes:%s>''' % (spatial_operator, geometryname, self._getGMLGeom(ewkt), distance, spatial_operator)
                
    def _getGMLGeom(self, ewkt):
        '''
        Returns a gml geometry for use in WFS spatial filtering.
        
        Does NOT support geometries of the MULTI type.
        '''
        
        _wkt = self._WKTParser()
        _wktGeomType, _posLists = _wkt(ewkt.split(';')[1], True)
        _posList = _posLists[0]
        
        if _wktGeomType == "point":
            return '''<gml:Point gml:id="P1" srsName="%s"><gml:pos>%s</gml:pos></gml:Point>''' % (self._get_srsName(ewkt), _posList)
        if _wktGeomType == "linestring":
            return '''<gml:Linestring gml:id="P1" srsName="%s"><gml:posList>%s</gml:posList></gml:Linestring>''' % (self._get_srsName(ewkt), _posList)
        if _wktGeomType == "linestring":
            return '''<gml:Polygon gml:id="P1" srsName="%s"><gml:posList>%s</gml:posList></gml:Polygon>''' % (self._get_srsName(ewkt), _posList)
                
    def execute(self, subject):
        ''' 
        Executes the test.

        `subject`       is expected a dict containing at least:
        
        - `geometry`    the geometry of the subject in EWKT. eg. `"SRID=28992;POINT(138034.181 452694.342)"`.
                        the MULTI variant of geometry types is not supported.
                     
        '''

        _distance = None
        if self.definition['distance']:
            _distance = self.definition['distance']
        
        _operator = self._SpatialOperator(self.definition['spatial_operator'], subject['geometry'], self.definition['geometryname'], _distance)
        _filter = self._Filter() % _operator
        _query = self._Query(self.definition['namespace'], self.definition['typename']) % _filter
        payload = self._getFeature() % _query

        self.logger.debug("Sending WFS-query to: " + self.definition['url'])
        self.logger.debug(payload)
        try:
            r = requests.post(url = self.definition['url'], data=payload, headers={'Content-Type': 'application/xml'})
        except Exception as error:
            self.logger.debug(traceback.format_exc())
            return self._handle_execution_exception( subject, 'Failed WFS request with error: ' + str(error) )

        tmp_folder = tempfile.mkdtemp()
        gml_file = os.path.join(tmp_folder,"response.gml")
        with open(gml_file, 'wb') as f:
            f.write(r.content)

        gdal.UseExceptions() 
        dataSource = ogr.Open(gml_file)
        layer = dataSource.GetLayer()
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

        shutil.rmtree(tmp_folder)

        self.executed = True                                                                # don't forget to set self.executed to True, 
                                                                                            # otherwise "Error: test is not executed:" will be added to the report as well

        return self._finish_execution(subject)                                              # Returns False to end execution or the subject to continue to the next test 
