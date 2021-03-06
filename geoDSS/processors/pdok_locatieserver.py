# -*- coding: utf-8 -*-


import json
import re

import requests

try:
    import exceptions
except:
    pass

from ..processors.processor import processor
from ..processors.processor import utils

class pdok_locatieserver(processor):
    '''
    This processor provides a geocoder using the Dutch PDOK locatieserver.

    Geocoding is done on zip-code and house_number of the subject.
    This geocoder takes the first hit as a result.
    
    Result
    ------
    
    Keys added to the subject on success:
    
    `geometry`                          The EWKT geometry obtained by geocoding the subject

    Definition
    ----------

    `definition` is expected to be a dict having:

     `url` (string):                    base url for the geocoder

     `report_template` (string):        (optional) String (with markdown support) to be reported on success.
                                        The following placeholders will be replaced

     - `subject.geometry`               the geometry which resulted from the geocoding process.
     - `{address}`                      the found address.
     - `{x}`                            the x coordinate of the found location.
     - `{y}`                            the y coordinate of the found location.
     - `{wkt_geometry}`                 the WKT geometry presentation of the found location.
     - `{ewkt_geometry}`                the EWKT geometry presentation of the found location.

    Rule example
    ------------

    a suitable yaml snippet would be:

        rules:
            geocode_address:
                type: processors.pdok_locatieserver
                title: Geocodeer adres
                description: Geocodeer adres op basis van postcode huisnummer
                url: "https://geodata.nationaalgeoregister.nl/locatieserver/v3/free?q="
                report_template: "Gevonden {address} op ['subject.geometry'](https://bagviewer.kadaster.nl/lvbag/bag-viewer/index.html#?geometry.x={x}&geometry.y={y}&zoomlevel=7)"

    Subject example
    ---------------

    a suitable subject would be:

        subject = '{"postcode": "4171KG", "huisnummer": "74"}'
    '''


    def execute(self, subject):
        '''
        Executes the geocoder.

        `subject` is expected to be a dict having:

        `postcode` (string):              zip-code or postal code

        `huisnummer` (string)             house number
        
            
        Result
        ------
    
        Keys added to the subject on success:
    
        `geometry`                          The EWKT geometry obtained by geocoding the subject.
        '''

        try:
            url = self.definition['url'] + subject['postcode'] + '-' + str(subject['huisnummer'])
            self.logger.debug("Geocoding with url: " + url)
            response = requests.get(url)
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not geocode address with error: `%s`" % str(error))
        else:
            if response.status_code == requests.codes.ok:
                self.logger.debug("Debugger returned status code: " + str(response.status_code))
                try:
                    try:
                        result = response.json()
                    except:
                        result = json.loads(response.content)                   # workaround for old requests libraries
                    if result["response"]["numFound"] > 0:
                        doc = result["response"]["docs"][0]
                        _wkt = utils.wkt._WKTParser()
                        _posLists = _wkt(doc["centroide_rd"])
                        XY = _posLists[0].split()
                        if XY:
                            x = float(XY[0])
                            y = float(XY[1])
                            wkt_geometry = 'POINT(%s %s)' % (x, y)
                            ewkt_geometry = 'SRID=28992;' + wkt_geometry
                            subject['geometry'] = ewkt_geometry 
                            self.executed = True
                    else:
                        return self._handle_execution_exception(subject, "Could not geocode address. The geocoder returned no matches.")
                except Exception as error:
                    return self._handle_execution_exception(subject, "Could not geocode address. Response parsing failed with error: " + str(error))
                address = None
                try:
                    address = doc["weergavenaam"]
                except Exception as error:
                    self.logger.debug('Could find position but not an address due to error: ' + str(error))
            else:
                return self._handle_execution_exception(subject, "Could not geocode address. Geocoder returned status code: `%s`" % str(response.status_code))

        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('subject.geometry', subject['geometry'])
            result = result.replace('{x}', str(x)).replace('{y}', str(y))
            result = result.replace('{wkt_geometry}', wkt_geometry)
            result = result.replace('{ewkt_geometry}', ewkt_geometry)
            if address:
                result = result.replace('{address}', address)
            else:
                result = result.replace('{address}', 'address not known')
            self.result.append(result)

        return self._finish_execution(subject)
