# -*- coding: utf-8 -*-

import re
import traceback

try:
    #python2
    from urllib import urlencode
except ImportError:
    #python3
    from urllib.parse import urlencode


from ..tests.test import test

class get_map(test):
    '''
    This test constructs a WMS GetMap request url to put in the report.
    This is usefull for adding a map to the report 

    Definition
    ----------

    `definition`     is expected to be a dict having at least:

    `url`            service endpoint for the GetMap request

    `params`         a dict with al params for a GetMap request (except the dynamic one: BBOX and SRS).
                     this dict will contain at least:
    - `width`        the width of the image (in pixels)
    - `height`       the height of the image (in pixels)
    - `layers`       the layers parameter of a GetMap request
    - `styles`       the styles paramater of a GetMap request (may be left empty)
    - `format`       the output format
    - `version`      WMS version

    `buffer`         The buffer around the subjects geometry (in map units)

    `flip_axes`      (optional) When using WMS 1.3.0 specify True if EPSG code and service requires the BBOX to be ymin,xmin,ymax,xmax

    `report_template` (string):           An emty string ("")

    Rule example
    ------------

    a useful yaml snippet for this test would be:

        rules:
            unit_test:
                type: tests.get_map
                title: The gelocated location
                description: A map illustrating where we found the address
                report_template: ""

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

    def _get_bbox(self, ewkt):
        '''
        A private method getting the bounding box of an EWKT string
        '''

        _wkt = self._WKTParser()
        _wktGeomType, _posLists = _wkt(ewkt.split(';')[1], True)
        bbox = [99999999,99999999,-99999999,-99999999]
        for pair in _posLists:
            x,y = pair.strip().split()
            x = float(x)
            y = float(y)
            if x < bbox[0]:
                bbox[0] = x
            if x > bbox[2]:
                bbox[2] = x
            if y < bbox[1]:
                bbox[1] = y
            if y > bbox[3]:
                bbox[3] = y

        self.logger.debug(str(bbox))
        return bbox

    def _buffer(self, bbox, distance, width = None, height = None):
        '''
        A private method buffering a bbox
        '''

        bbox[0] = bbox[0] - distance
        bbox[2] = bbox[2] + distance
        if width and height:
            new_width = bbox[2] - bbox[0]
            new_height = new_width * height / width
            distance = (new_height - (bbox[3] - bbox[1])) / 2
        bbox[1] = bbox[1] - distance
        bbox[3] = bbox[3] + distance

        return bbox

    def _get_srs(self, ewkt, version = '1.3.0'):
        '''
        A private method to get a proper crs/ srs parameter for the WMS request
        '''

        code = ewkt.split(';')[0].split('=')[1].strip()
        if version == '1.3.0':
            return 'CRS', 'EPSG:%s' % str(code)
        else:
            return 'SRS', 'EPSG:%s' % str(code)


    def execute(self, subject):
        ''' 
        Executes the test.

        `subject`       is expected a dict containing at least:
        
        - `geometry`    the geometry of the subject in EWKT. eg. `"SRID=28992;POINT(138034.181 452694.342)"`.
                        the MULTI variant of geometry types is not supported.
                     
        '''

        params = self.definition['params']
        try:
            bbox = self._buffer(self._get_bbox(subject['geometry']), self.definition["buffer"])
            params['bbox'] = bbox
            if 'flip_axes' in self.definition and self.definition['flip_axes']:
                params['bbox'][0] = bbox[1]
                params['bbox'][1] = bbox[0]
                params['bbox'][2] = bbox[3]
                params['bbox'][3] = bbox[2]
            params['bbox'] = ','.join(map(str, params['bbox']))
        except Exception as error:
            self.logger.debug(traceback.format_exc())
            return self._handle_execution_exception( subject, 'Could not create bbox from geometry with error: ' + str(error) )

        try:
            url = self.definition['url']
            params = self.definition["params"]
            params['service'] = 'WMS'
            params['request'] = 'GetMap'
            key, value = self._get_srs(ewkt = subject['geometry'], version = params["version"])
            params[key] = value
            qs = urlencode(params)
        except Exception as error:
            self.logger.debug(traceback.format_exc())
            return self._handle_execution_exception( subject, 'Could not create query string due to error: ' + str(error) )

        
        if '?' in url:
            if not url[-1] == '&':
                url = url + '&'
            url = url + qs
        else:
            url = url + '?' + qs

        self.decision = True                                                                # don't forget to set self.decision to True,
                                                                                            # otherwise "Test decision is: False" is added to the report instead of the following:

        self.result.append("![Map](%s)" % url )                                         
        
        self.executed = True                                                                # don't forget to set self.executed to True, 
                                                                                            # otherwise "Error: test is not executed:" will be added to the report as well

        return self._finish_execution(subject)                                              # Returns False to end execution or the subject to continue to the next test 
