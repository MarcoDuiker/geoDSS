#!/usr/bin/env python
#!C:/Python27/python.exe -u
# -*- coding: utf-8 -*-

'''
This example code shows how easy it is to run geoDSS in a scheduled manner. 
Of course this example is functional, but might be improved on with eg. more error checking, logging and communication
with the user.

eg. ./schedule.py examples/rule_sets/scheduled_request.yaml examples/subjects/google_request.json 10 seconds ./scheduled_run_results.csv
'''

import argparse
import glob
import json
import marshal
import os
import string
import sys
import time
import traceback


try:
    import exceptions
except:
    pass
    
import schedule

# make sure we can import the package when run as script
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import geoDSS
from geoDSS import reporters
from geoDSS import loaders

class _VersionedOutputFile:
    '''
    This is like a file object opened for output, but it makes
    versioned backups of anything it might otherwise overwrite.
    '''

    # http://code.activestate.com/recipes/52277-saving-backups-when-writing-files/
    
    def __init__(self, pathname, numSavedVersions=0):
        '''
        Create a new output file.
        
        `pathname` is the name of the file to [over]write.
        `numSavedVersions` tells how many of the most recent versions
        of `pathname` to save.
        '''
        
        self._pathname = pathname
        self._tmpPathname = "%s.~new~" % self._pathname
        self._numSavedVersions = numSavedVersions
        self._outf = open(self._tmpPathname, "wb")

    def __del__(self):
        self.close()

    def close(self):
        if self._outf:
            self._outf.close()
            self._replaceCurrentFile()
            self._outf = None

    def asFile(self):
        """
        Return self's shadowed file object, since marshal is
        pretty insistent on working w. pure file objects.
        """
        
        return self._outf

    def __getattr__(self, attr):
        """
        Delegate most operations to self's open file object.
        """
        
        return getattr(self.__dict__['_outf'], attr)
    
    def _replaceCurrentFile(self):
        """
        Replace the current contents of self's named file.
        """
        
        self._backupCurrentFile()
        os.rename(self._tmpPathname, self._pathname)

    def _backupCurrentFile(self):
        """
        Save a numbered backup of self's named file.
        """
        # If the file doesn't already exist, there's nothing to do.
        if os.path.isfile(self._pathname):
            newName = self._versionedName(self._currentRevision() + 1)
            os.rename(self._pathname, newName)

            # Maybe get rid of old versions.
            if ((self._numSavedVersions is not None) and
                (self._numSavedVersions > 0)):
                self._deleteOldRevisions()

    def _versionedName(self, revision):
        """
        Get self's pathname with a revision number appended.
        """
        
        return "%s.~%s~" % (self._pathname, revision)
    
    def _currentRevision(self):
        """
        Get the revision number of self's largest existing backup.
        """
        
        revisions = [0] + self._revisions()
        return max(revisions)

    def _revisions(self):
        """Get the revision numbers of all of self's backups."""
        
        revisions = []
        backupNames = glob.glob("%s.~[0-9]*~" % (self._pathname))
        for name in backupNames:
            try:
                revision = int(string.split(name, "~")[-2])
                revisions.append(revision)
            except ValueError:
                # Some ~[0-9]*~ extensions may not be wholly numeric.
                pass
        revisions.sort()
        return revisions

    def _deleteOldRevisions(self):
        """
        Delete old versions of self's file, so that at most
        self._numSavedVersions versions are retained.
        """
        
        revisions = self._revisions()
        revisionsToDelete = revisions[:-self._numSavedVersions]
        for revision in revisionsToDelete:
            pathname = self._versionedName(revision)
            if os.path.isfile(pathname):
                os.remove(pathname)



def execute_and_report(rule_set, subject, output_file, num_backups = 3):
    '''
    Run a subject against a rule_set scheduled.
    The rule_set is reported only once, and the report fo the rules will be appended to the output file.
    '''
    
    try:
        rule_set.execute(subject)
    except Exception as e:
        print("geoDSS: could not execute rule with subject due to an error: " + str(e))
    else:
        outf = _VersionedOutputFile(output_file, num_backups)
        outf.write(rule_set.report())                       # reports accumulate as long as we don't re-initialize the geoDSS.rules_set
        outf.close()
    
def schedule_geoDSS(rule_set_file, subject, output_file, interval = 1, units = "hours", at = "00.00", for_minutes = 0, for_hours = 0, num_backups = 0):
    '''
    Run geoDSS scheduled.
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
    
    if os.path.exists(args.subject):
        with open(args.subject, 'r') as f:
            subject_string = f.read()
    else:
        subject_string = args.subject
    subject = json.loads(subject_string)   
    
    if os.path.exists(output_file):
        os.remove(output_file)
        
    if units == "months":
        schedule.every(interval).months.do(execute_and_report, rule_set = r, subject = subject, output_file = output_file, num_backups = num_backups)
    elif units == "weeks":
        schedule.every(interval).weeks.do(execute_and_report, rule_set = r, subject = subject, output_file = output_file, num_backups = num_backups)
    elif units == "days":
        schedule.every(interval).days.at(at).do(execute_and_report, rule_set = r, subject = subject, output_file = output_file, num_backups = num_backups)
    elif units == "hours":
        schedule.every(interval).hours.do(execute_and_report, rule_set = r, subject = subject, output_file = output_file, num_backups = num_backups)
    elif units == "minutes":
        schedule.every(interval).minutes.do(execute_and_report, rule_set = r, subject = subject, output_file = output_file, num_backups = num_backups)
    elif units == "seconds":
        schedule.every(interval).seconds.do(execute_and_report, rule_set = r, subject = subject, output_file = output_file, num_backups = num_backups)

    period_to_run = None
    if for_minutes:
        period_to_run = for_minutes * 60
    if for_hours:
        period_to_run = for_hours * 60 * 60
        
    start_time = time.time()
    
    finished = False
    while not finished:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            exit()
        if period_to_run and time.time() - start_time > period_to_run:
            finished = True
                
                
if __name__ == '__main__':
    '''
    Command line ultility to run geoDSS scheduled.
    This will block the terminal, so use something like screen if you want it
    to keep running.
    '''
    
    # todo: add an "until" (eg. certain date) option.

    parser = argparse.ArgumentParser(description = 'Invoke geoDSS in batch mode using the plain text reporter.',
                                     epilog =      '''Example: ./schedule.py examples/rule_sets/scheduled_request.yaml examples/subjects/google_request.json 10 seconds ./scheduled_run_results.csv ''')
    parser.add_argument("rule_set_file",                            help = 'The file containing the rule set.')
    parser.add_argument("subject",                                  help = 'Either a JSON-string defining a python dict containing a subject or a path to a file containing such a JSON-string.')
    parser.add_argument("interval", type=int,                       help = 'Interval to run at.')
    parser.add_argument("units", choices=("months","weeks","days","hours","minutes","seconds"),  
                                                                    help = 'Units in which interval is specified.')
    parser.add_argument("output_file",                              help = 'An output file to write the results to.')
    parser.add_argument("--at",                                     help = 'A specific moment on a day to run, specified as string: HH:MM. defaults to 00.00')
    parser.add_argument("--num_backups", type = int, default = 0,   help = 'The number of backups kept when saving a new output_file.')
    
    during_group = parser.add_mutually_exclusive_group()
    during_group.add_argument("--for_minutes", type = int,          help = 'The number of minutes to run for.')
    during_group.add_argument("--for_hours", type = int,            help = 'The number of hours to run for.')
  
    args = parser.parse_args()

    schedule_geoDSS(rule_set_file = args.rule_set_file, subject = args.subject, interval = args.interval, units=args.units,
                    for_minutes = args.for_minutes, for_hours = args.for_hours,
                    output_file = args.output_file, num_backups = args.num_backups)
