# -*- coding: utf-8 -*-

import requests
from xml.dom import minidom
from xml.dom.minidom import parseString

try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class bag_geocoder(processor):
    '''
    This processor provides geocoder using the BAG geocoding service.

    Geocoding is done on zip-code and house_number of the subject. 
    This geocoder takes the first hit as a result

    definition is expected to be a dict having:
        url (string):                       base url for the geocoder
        report_template (format string):    (optional) Python format string with markdown support to be reported when geocoding is a succes. 
                                            If the format string contains subject.geometry it will be replaced by the geometry which resulted from the geocoding process.

    a suitable yaml snippet would be:
        rules:
            geocode_address:
                type: processors.bag_geocoder
                title: Geocodeer adres
                description: Geocodeer adres op basis van postcode huisnummer
                url: "http://geodata.nationaalgeoregister.nl/geocoder/Geocoder?zoekterm="
                report_template: "Gevonden coordinaten: subject.geometry"

    a suitable subject would be:
        subject = '{"postcode": "4171KG", "huisnummer": "74"}'
    '''

    def execute(self, subject):
        '''
        executes the geoocder

        subject is expected to be a dict having:
            postcode (string):              zip-code or postal code
            huisnummer (string)             house number
        '''

        try:
            url = self.definition['url'] + subject['huisnummer'] + '+' + subject['postcode']
            self.logger.debug("Geocoding with url: " + url)
            response = requests.get(url)
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not geocode address with error: `%s`" % str(error) )
        else:
            if response.status_code == requests.codes.ok:
                self.logger.debug("Debugger returned status code: " + str(response.status_code))
                try:
                    doc = parseString(response.text)
                    positionsList = doc.getElementsByTagName("gml:pos")
                    if positionsList:
                        xmlTag = positionsList[0].firstChild.nodeValue
                        XY = xmlTag.split()
                        if XY:
                            x = float(XY[0])
                            y = float(XY[1])
                            subject['geometry'] = 'SRID=28992;POINT(%s %s)' % (x,y)
                            self.executed = True
                    else:
                        return self._handle_execution_exception(subject, "Could not geocode address. The geocoder returned no matches." )
                except Exception as error:
                    return self._handle_execution_exception(subject, "Could not geocode address. Response parsing failed with error: " + str(error) )
                address = None
                try:
                    address_element = doc.getElementsByTagName("xls:Address")[0]
                    street_element = address_element.getElementsByTagName("xls:StreetAddress")[0]
                    house_number = street_element.childNodes[0].getAttribute('number')
                    house_number = house_number + street_element.childNodes[0].getAttribute('subdivision')
                    street = street_element.childNodes[1].firstChild.data
                    places_list = []
                    places = address_element.getElementsByTagName("xls:Place")
                    for p in places:
                        places_list.append(p.firstChild.data)
                    address = street + ' ' + house_number + ' ' + ', '.join(places_list)
                except Exception as error:
                    self.logger.debug('Could find position but not an address due to error: ' + str(error) )  
            else:
                return self._handle_execution_exception(subject, "Could not geocode address. Geocoder returned status code: `%s`" % str(response.status_code) )

        if self.executed and  self.definition["report_template"]:
            result = self.definition["report_template"].replace('subject.geometry', subject['geometry'])
            if address:
                result = result.replace('{address}', address)
            else:
                result = result.replace('{address}', 'address not known')
            self.result.append(result)

        return self._finish_execution(subject)
