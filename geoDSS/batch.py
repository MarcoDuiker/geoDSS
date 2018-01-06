#!/usr/bin/env python
#!C:/Python27/python.exe -u
# -*- coding: utf-8 -*-

'''
This example code shows how easy it is to run geoDSS against multiple subjects loaded from a csv file. 
Of course this example is functional, but might be improved on with eg. more error checking, logging and communication
with the user.

eg. ./batch.py examples/rule_sets/batch_geocode_tab.yaml examples/subjects/batch_geocode.csv ./batch_result.csv
'''

import argparse
import csv
import os
import sys
import traceback

try:
    import exceptions
except:
    pass

# make sure we can import the package when run as script
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import geoDSS
from geoDSS import reporters
from geoDSS import loaders


def batch_execute(rule_set_file, subject_file, output_file):
    '''
    
    '''
    
    base_name,extension = os.path.splitext(rule_set_file)

    loader_module = loaders.yaml_loader
    if extension == '.json':
        loader_module = loaders.json_loader

    try:
        r = geoDSS.rules_set(rule_set_file, loader_module)
    except Exception as e:
        print("geoDSS: Could not load rule_set with error: %s " % str(e))
        print(traceback.format_exc())
        return
       
    with open(subject_file, 'rb') as f:
        reader = csv.DictReader(f)
        for subject in reader:
            try:
                r.execute(subject)
            except Exception as e:
                print("geoDSS: Could not evaluate rule_set with error: %s" % str(e))
                print(traceback.format_exc())
                
    with open(output_file, 'wb') as of: 
        of.write(r.report())                        # reports accumulate as long as we don't re-initialize the geoDSS.rules_set
                
                
if __name__ == '__main__':
    '''


    '''

    parser = argparse.ArgumentParser(description = 'Invoke geoDSS in batch mode using the plain text reporter.',
                                     epilog =      '''Example: ./batch.py examples/rule_sets/batch_geocoder_test.yaml batch_geocode.csv ./test_output.csv ''')
    parser.add_argument("rule_set_file",                            help = 'The file containing the rule set.')
    parser.add_argument("subject_file",                             help = 'A csv file containing subjects.')
    parser.add_argument("output_file",                              help = 'An output file to write the results to.')
    
    args = parser.parse_args()

    batch_execute(rule_set_file = args.rule_set_file, subject_file = args.subject_file, output_file = args.output_file)
