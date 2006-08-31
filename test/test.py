#!/usr/bin/env python
##
## Biskit, a toolkit for the manipulation of macromolecular structures
## Copyright (C) 2004-2005 Raik Gruenberg & Johan Leckner
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You find a copy of the GNU General Public License in the file
## license.txt along with this program; if not, write to the Free
## Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##
## last $Author$
## last $Date  $
## $Revision$

import Biskit.Test as Test

import unittest
import re, sys
import Biskit.tools as T


o = {'log':T.projectRoot()+'/test/test.log',
     'verb':2,
     'tests': ['all', 'exclude_long'] }


def _use():
    print """
    Run unittest tests for biskit.

    log   - str, path to logfile that will be written
    verb  - int, verbosity level
    tests - [str], list of the test suits to be run, one or more of::
    
               biskit         - most Biskit modules
               biskit_app     - Biskit modules calling external applications
               biskit_pvm     - Biskit modules using PVM
               dock           - most Biskit.Dock modules
               dock_app       - Biskit.Dock modules calling
                                  external applications
               dock_app_long  - time-consuming Biskit.Dock modules calling
                                  external applications (full test)
               dock_pvm       - Biskit.Dock modules using PVM
               mod            - all Biskit.Mod modules
               mod_long       - time-consuming Biskit.Mod modules (full test)
               dock_pvm       - Biskit.Dock modules using PVM
               dock_pvm_long  - time-consuming Biskit.Dock modules
                                  using PVM (full test)
               stat           - Biskit.Statistics modules
               pvm            - Biskit.PVM modules
               
            Or one or more of the groups::

               all         - all tests
               all_mod     - all Biskit.Mod tests
               all_dock    - all Biskit.Dock tests 
               all_biskit  - all Biskit tests

            To exclude tests::
            
               exclude_long  - don't run time-consuming tests
               exclude_pvm   - dont run tests using PVM

        
Default options:
"""
    for key, value in o.items():
        print "\t-",key, "\t",value
        
    sys.exit(0)

    
############################################
## Create test suits


## Biskit
def suite_biskit():
    suite = unittest.makeSuite( Test.Biskit )
    return suite

def suite_biskit_applications():
    suite = unittest.makeSuite( Test.Biskit_Applications )
    return suite

def suite_biskit_pvm():
    suite = unittest.makeSuite( Test.Biskit_Pvm )
    return suite


## Biskit.Dock
def suite_dock():
    suite = unittest.makeSuite( Test.Dock )
    return suite

def suite_dock_applications():
    suite = unittest.makeSuite( Test.Dock_Applications )
    return suite

def suite_dock_applications_long():
    suite = unittest.makeSuite( Test.Dock_Applications_Long )
    return suite

def suite_dock_pvm():
    suite = unittest.makeSuite( Test.Dock_Pvm )
    return suite


## Biskit.Mod
def suite_mod():
    suite = unittest.makeSuite( Test.Mod )
    return suite

def suite_mod_long():
    suite = unittest.makeSuite( Test.Mod_Long )
    return suite

def suite_mod_pvm():
    suite = unittest.makeSuite( Test.Mod_Pvm )
    return suite

def suite_mod_pvm_long():
    suite = unittest.makeSuite( Test.Mod_Pvm_Long )
    return suite


## Biskit.Statistics
def suite_statistics():
    suite = unittest.makeSuite( Test.Statistics )
    return suite


## Biskit.PVM
def suite_pvm_depending():
    suite = unittest.makeSuite( Test.Pvm )
    return suite



############################################
## Create a report


def report( file ):
    """
    Parses the log file and collects some data.
    
    @param file: log-file path
    @type  file: str

    @return: the log, list of failed tests, number of tests and number of passed tests
    @rtype: [str], [str], int, int
    """
    r = open(file,'r')
    test_result = r.readlines()
    r.close()

    ## full log message
    full_log = ['\n', '='*60+'\n', '======= TEST RESULTS\n', '='*60 +'\n' ]

    ## collect failed
    failed = []

    count, passed  = 0, 0

    ## parse log file
    for line in test_result:
        if line != '\n':
            
            full_log += [line]

            ## count tests
            if re.match('^test_.*', line):
                count += 1

            ## count passed tests
            if re.match('^test_.*ok$', line):
                passed += 1            

            ## collect failed/error info
            if re.match('.*FAIL$', line) or re.match( '.*ERROR$', line):
                failed += [ line ]

    return full_log, failed, count, passed
            

############################################
## Main

if __name__ == '__main__':

    if sys.argv[-1].upper() in ['H', '-H', 'HELP', '-HELP']:   
        _use()
        sys.exit(0)
    
    o = T.cmdDict( o )


##     o = {'log':T.projectRoot()+'/test/test.log',
##          'verb':2,
##          'tests': ['stat','biskit'] }

    log = T.absfile( o['log'] )
    verb = T.toInt( o['verb'] )


    ################################
    ## determine what tests to run
    tests = T.toList( o['tests'] )

    if 'all' in tests:
        tests += [ 'all_biskit', 'all_mod', 'all_dock', 'stat', 'pvm' ]
        tests.remove('all')
        
    if 'all_biskit' in tests:
        tests += [ 'biskit', 'biskit_app', 'biskit_pvm' ]
        tests.remove('all_biskit')
        
    if 'all_mod' in tests:
        tests += [ 'mod', 'mod_long' ]
        tests.remove('all_mod')
        
    if 'all_dock' in tests:
        tests += ['dock', 'dock_app', 'dock_app_long', 'dock_pvm']
        tests.remove('all_dock')
        
    if 'exclude_long' in tests:
        for t in tests:
            if re.match('.*long.*', t):
                tests.remove(t)
        
    if 'exclude_pvm' in tests:
        for t in tests:
            if re.match('.*pvm.*', t):
                tests.remove(t)        

    for t in tests:
        if re.match('pvm', t):
            print '\nNOTE:\n=====\n Tests involving modules that depend on the PVM deamon have been selected. Make sure that PVM is running.\n'


    ################################
    ## run tests
    f=open( log, 'w')
    
    runner = unittest.TextTestRunner( f, verbosity=verb )

    ## Biskit
    if 'biskit' in tests:
        f.write('\nTESTS FOR BISKIT MODULES:\n')
        runner.run( suite_biskit() )

    if 'biskit_app' in tests:    
        f.write('\nTESTS FOR BISKIT MODULES CALLING EXTERNAL APPLICATIONS:\n')
        runner.run( suite_biskit_applications() )

    if 'biskit_pvm' in tests:    
        f.write('\nTESTS FOR BISKIT MODULES THAT USE PVM:\n')
        runner.run( suite_biskit_pvm() )

    ## Biskit.Dock    
    if 'dock' in tests:
        f.write('\nTESTS FOR BISKIT.DOCK MODULES:\n')
        runner.run( suite_dock() )

    if 'dock_app' in tests:
        f.write('\nTESTS FOR BISKIT.DOCK MODULES CALLING EXTERNAL APPLICATIONS:\n')
        runner.run( suite_dock_applications() )

    if 'dock_app_long' in tests:
        f.write('\nTESTS FOR BISKIT.DOCK MODULES THAT ARE TIME-CONSUMING AND CALL EXTERNAL APPLICATIONS :\n')
        runner.run( suite_dock_applications_long() )

    if 'dock_pvm' in tests:    
        f.write('\nTESTS FOR BISKIT.DOCK MODULES THAT USE PVM:\n')
        runner.run( suite_dock_pvm() )


    ## Biskit.Mod    
    if 'mod' in tests:
        f.write('\nTESTS FOR BISKIT.MOD MODULES:\n')
        runner.run( suite_mod() )

    if 'mod_long' in tests:
        f.write('\nTESTS FOR BISKIT.MOD MODULES THAT ARE TIME-CONSUMING:\n')
        runner.run( suite_mod_long() )

    if 'dock_pvm' in tests:    
        f.write('\nTESTS FOR BISKIT.DOCK MODULES THAT USE PVM:\n')
        runner.run( suite_mod_pvm() )

    if 'dock_pvm_long' in tests:    
        f.write('\nTESTS FOR BISKIT.DOCK MODULES THAT ARE TIME-CONSUMING AND USE PVM:\n')
        runner.run( suite_mod_pvm_long() )

        
    ## Biskit.Statistics    
    if 'stat' in tests:
        f.write('\nTESTS FOR BISKIT.STATISTICS MODULES:\n')
        runner.run( suite_statistics() )


    ## Biskit.PVM    
    if 'pvm' in tests:
        f.write('\nTESTS FOR MODULES USING PVM:\n')
        runner.run( suite_pvm_depending() )

    f.close()


    ##################################
    ## report how things went
    
    lines, failed, count, passed = report( log )

    ## print full log file
    for line in lines:
        print line[:-1]
    print '\nThe test log file have been saved to: %s'%log

    
    ## print a summary
    print '\nSUMMARY:\n=======\n'
    print 'A total of %i tests were run.'%passed
    print '   - %i passed'%passed    
    print '   - %i failed'%len(failed)

    ## and a better message about which module failed 
    if len(failed) > 0:
        for f in failed:

            l = f.split()
            m = l[1].strip('()').split('.')[-1] # strip off "Biskit.Test"
            
            # get failed test doc string
            doc_str = vars()['Test'].__dict__[m].__dict__[l[0]].__doc__

            # parse module info from doc string
            module = re.findall( 'L\{(Biskit[A-Za-z\._\s]*)\}', doc_str.strip() )
            
            print '      - test in module %s failed'%module[0]


    


