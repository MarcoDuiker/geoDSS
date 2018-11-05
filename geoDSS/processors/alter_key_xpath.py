# -*- coding: utf-8 -*-


from contextlib import contextmanager

from lxml import html

try:
    import exceptions
except:
    pass

from ..processors.processor import processor


class alter_key_xpath(processor):
    '''
    This processor alters a subject key by executing an xpath expression against
    a subject key. As namespacing is not supported, this is most useful for html.
    
    Dependencies
    ------------
    
    - lxml
    
    Result
    ------
    
    Keys in the subject on changed by success:
    
    The key which is added/ changed is determined by the definition in the rule set (`result_key`).
    

    Definition
    ----------

    `definition` is expected to be a dict having:
    
     `subject_key` (string):            The name of the key to run the xpath expression against.
                                        Mostly this will contain html.

     `result_key` (string):             The name of the key to store the result.
                                        If the key exists, the existing value will be overwritten.
                                        Otherwise a new key will be added.
     
     `expression` (string):             The python xpath-expression to execute against the subject_key. 
                                        If expression is a key in the subject then the expression will be 
                                        taken from that key in the subject.
                                        
     `delimiter` (string):              The items in the result set will be delimited by this string. Defaults to `;`.
     
     `report_template` (string):        (optional) String (with markdown support) to be reported on success.

                                        The following placeholders will be replaced:
    
     - `{result}`                       The resulting value from the proces.


    Rule example
    ------------

    a suitable yaml snippet would be:

        rules:
        - example:
            type: processors.alter_key_xpath
            title: Alter a key
            description: ""
            result_key: url
            expression: subject['url'].replace(' ','%20')
            report_template: "Generated a new key: {result}"

    
    Subject example
    ---------------

    Any subject will do, so this one as well:

        subject = '{"url": "a stupid url with spaces.com"}'
    '''
    

    def execute(self, subject):
        '''
        Executes the processor.

        `subject` can be any dict.
        
        Result
        ------
        
        Keys changed or added to the subject on success.
        '''
        
        delimiter = ';'
        if 'delimiter' in self.definition:
            delimiter = self.definition['delimiter']
        
        try:
            expression = self.definition["expression"]
            if expression in subject:
                expression = subject[expression]
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not get expression from the definition with error: `%s`" % str(error))
            
        try:
            tree = html.fromstring(subject[self.definition['subject_key']])
            result = tree.xpath( expression )
            if result:                  
                result = delimiter.join(result)
            else:
                result = ""
            subject[self.definition['result_key']] = result
        except Exception as error:
            return self._handle_execution_exception(subject, "Could not execute expression with error: `%s`" % str(error))

        self.executed = True
        if self.executed and self.definition["report_template"]:
            result = self.definition["report_template"].replace('{result}', str(result))
            self.result.append(result)

        return self._finish_execution(subject)
