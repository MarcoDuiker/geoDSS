# -*- coding: utf-8 -*-

import re
import traceback

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

    `report_template` (string):     A string containing {url}. {url} will be replaced by the WMS GetMap request url. 
                                    After that, any specified {key} from the subject will be substituted by its value as well.
                                    
        When using the html output of the standard markdown reporter a semi opaque red box indicating the middle of the 
        image can be added by providing an alt text like this:
                                    
            `report_template`: "![Centered_map_small]({url})"

            _small, _medium and _large refer to the image size. If no red box appears, go one size up.

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

    def _buffer(self, bbox, distance, width = None, height = None):
        '''
        A private method buffering a bbox. Aspect ratio is adjusted to the width and height of the image when given.
        '''

        bbox[0] = bbox[0] - distance
        bbox[2] = bbox[2] + distance
        if width and height and not width == height:
            if width > height:
                new_width = bbox[2] - bbox[0]
                new_height = new_width * height / width
                distance = (new_height - (bbox[3] - bbox[1])) / 2
            else:
                new_height = bbox[3] - bbox[1]
                new_width = new_height * width / height
                distance = (new_width - (bbox[2] - bbox[0])) / 2
        bbox[1] = bbox[1] - distance
        bbox[3] = bbox[3] + distance

        return bbox

    def execute(self, subject):
        ''' 
        Executes the test.

        `subject`       is expected a dict containing at least:
        
        - `geometry`    the geometry of the subject in EWKT. eg. `"SRID=28992;POINT(138034.181 452694.342)"`.
                        the MULTI variant of geometry types is not supported.
                     
        '''

        params = self.definition['params']
        try:
            bbox = self._buffer(bbox = utils.wkt._get_bbox(subject['geometry']), 
                                distance = self.definition["buffer"], 
                                width = params["width"], 
                                height = params["height"] )
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

        result = self.definition["report_template"].replace('{url}', url)
        for key, value in subject.items():                               
            result = result.replace('{%s}' % (key), str(value))
        self.result.append(result)
        
        self.executed = True                                                                # don't forget to set self.executed to True, 
                                                                                            # otherwise "Error: test is not executed:" will be added to the report as well

        return self._finish_execution(subject)                                              # Returns False to end execution or the subject to continue to the next test 
