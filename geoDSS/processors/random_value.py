# -*- coding: utf-8 -*-

import random

try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class random_value(processor):
    '''
    This processor adds a random value to a key.
    
    Result
    ------
    
    Keys added to the subject on success:
    
    from_definition:                        The key which is added is determined by the definition.
    

    Definition
    ----------

    `definition` is expected to be a dict having:

     `random_value_key` (string):       The name of the key to add the random value to.
     
     `min` (number):                    The minimum value of the returned random value.
     
     `max` (number):                    The maximim value of the returned random value.

     `report_template` (string):        (optional) String (with markdown support) to be reported on success.

                                        The following placeholders will be replaced:
    
     - `{random_value}`                 The random value generated.


    Rule example
    ------------

    a suitable yaml snippet would be:

        rules:
        - x_coordinate:
          type: processors.random_value
          title: Random x-coordinate
          description: ""
          random_value_key: x
          min: 25000
          max: 30000
          report_template: "Generated the x-coordinate: {random_value}"

    
    Subject example
    ---------------

    Any subject will do, so this one as well:

        subject = '{"postcode": "4171KG", "huisnummer": "74"}'
    '''


    def execute(self, subject):
        '''
        Executes the random value generator.

        `subject` can be any dict.
        
        Result
        ------
        
        Keys added to the subject on success:
    
        from_definition:                        The key which is added is determined by the definition.
        '''

        try:
            v = random.uniform(self.definition['min'], self.definition['max'])
            subject[self.definition['random_value_key']] = v
        except Exception as error:
            return self._handle_execution_exception(subject, "Could generate random value with error: `%s`" % str(error))
        
        self.executed = True
        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('{random_value}', str(v))
            self.result.append(result)

        return self._finish_execution(subject)
