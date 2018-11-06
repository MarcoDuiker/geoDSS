# -*- coding: utf-8 -*-

'''
This module contains helper functions for (E)WKT manipulation.
'''

import re

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


def _get_bbox(ewkt):
    '''
    A private method getting the bounding box of an EWKT string
    '''

    _wkt = _WKTParser()
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

def _get_srs(ewkt, version = '1.3.0'):
    '''
    A private method to get a proper crs/ srs parameter for the WMS request
    '''

    code = ewkt.split(';')[0].split('=')[1].strip()
    if version == '1.3.0':
        return 'CRS', 'EPSG:%s' % str(code)
    else:
        return 'SRS', 'EPSG:%s' % str(code)
        
def _get_srsName(ewkt):
    '''
    A private method to get a proper srsName for the WFS request from an EWKT string
    '''

    code = ewkt.split(';')[0].split('=')[1].strip()
    return "urn:ogc:def:crs:EPSG::%s" % str(code)
    
def _get_SRID_string(ewkt):
    '''
    A private method to get the EWKT projection string from an EWKT string
    '''
    
    return ewkt.split(';')[0].strip()
    
def _get_WKT_geometry(ewkt):
    '''
    A private method to get the WKT geometry string from an EWKT string
    '''
    
    return ewkt.split(';')[1].strip()
    
def _EWKT_from_WKT(srid, wkt ):
    '''
    Private method to get a valid EWKT geometry string from a WKT string and a EWKT SRID string
    '''
    
    return ';'.join([srid,wkt])
    
def _getGMLGeom(ewkt):
    '''
    Private method. returns a gml geometry for use in WFS spatial filtering.
    
    Does NOT support geometries of the MULTI type.
    '''
    
    _wkt = _WKTParser()
    _wktGeomType, _posLists = _wkt(ewkt.split(';')[1], True)
    _posList = " ".join(_posLists)
    
    if _wktGeomType == "point":
        return '''<gml:Point gml:id="P1" srsName="%s"><gml:pos>%s</gml:pos></gml:Point>''' % (self._get_srsName(ewkt), _posList)
    if _wktGeomType == "linestring":
        return '''<gml:LineString gml:id="P1" srsName="%s"><gml:posList>%s</gml:posList></gml:LineString>''' % (self._get_srsName(ewkt), _posList)
    if _wktGeomType == "polygon":
        return '''<gml:Polygon gml:id="P1" srsName="%s"><gml:exterior><gml:LinearRing><gml:posList>%s</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon>''' % (self._get_srsName(ewkt), _posList)
    

