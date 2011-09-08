##
## Biskit, a toolkit for the manipulation of macromolecular structures
## Copyright (C) 2004-2011 Raik Gruenberg & Johan Leckner
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
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
## last $Author: graik $
## last $Date: 2009-05-09 14:17:28 +0200 (Sat, 09 May 2009) $
## $Revision: 742 $
"""
Read Amber residue topology from Amber "off" libraries.
"""
import cStringIO
import numpy as N
import os.path as osp
import re

import Biskit.tools as T
import Biskit as B
import Biskit.molUtils as M
 

class AmberResidueType( B.PDBModel ):
    """
    Standard description of a certain class of residues.
    """
    
    def __init__(self, name=None, code=None, letter=None, source=None  ):
        
        self.name = name      ## 'alanine'
        self.code = code      ## 'ALA'
        self.letter = letter  ## 'A'
        if self.name:
            self.name = self.name.lower()
        if self.code:
            self.code = self.code.upper()
        if self.letter:
            self.letter = self.letter.upper()
        
        B.PDBModel.__init__( self, source=source )
        
        if source:
            self.__fromPDB()
        

    def __fromPDB( self ):
        self.code = self.atoms['name'][0]        
        self.letter = M.singleAA( [ self.code ] )
        
        
    def __str__( self ):
        return '[%s %3s %3i atoms: %-20s ]' % \
               (self.__class__.__name__, self.code, len(self), self.name )
    
    def __repr__( self ):
        return str( self )
        
       
class AmberPrepParser( object ):
    """
    Parse Amber Residue libraries (off or prep files) which are usually found 
    in amber/dat/leap/prep.
    
    Usage::
    
        p = AmberOffParser( 'all_amino03.in' )
        residues = [ r for r in p.residueTypes() ]
    """
    
    F_DEFAULT = 'all_amino03.in'
    
    def __init__(self, f_in=None ):
        """
        @param f_in: amber "off" or "prep" file with residue definitions
                     if not existing, we will look for a file with this name
                     in the Biskit data folder (data/amber/residues)
                     (default: 'all_amino03.in')
        @type  f_in: str
        """
        f_in = f_in or self.F_DEFAULT
        if not osp.exists( T.absfile( f_in ) ):
            f_in = T.dataRoot() + '/amber/residues/' + f_in
        
        self.firstrecord = re.compile( 'db[0-9]+\.dat' )
        
        self.s = open( T.absfile( f_in ), 'r' ).read()
        self.s = self.firstrecord.split( self.s )[-1] #skip until first residue
  

    def residueBlocks( self ):
        i_from = 0
        i_to = self.s.find( 'DONE', i_from )

        while i_to != -1:
            yield self.s[i_from : i_to]
            i_from = i_to + 4
            i_to   = self.s.find( 'DONE', i_from )
            
    
    def atomLines( self, s ):
        """@param s: str, atom block
        """
        start = s.find('0.0')
        end = s.find( '\n\n', start + 10 )

        io = cStringIO.StringIO( s[start:end] )
        for i in range(4):
            io.readline()
        
        line = io.readline().strip()
        while line:
            yield line
            line = io.readline().strip()


    def parseCharges( self, s ):
        s = s[ s.find('CHARGE') : ]
        s = s[ s.find('\n') : ]
        s = s[ : s.find('IMPROPER') ]
        s = s.strip()
        r = N.array( s.split() )
        return r

    
    def parseResidue( self, s ):
        """@param s: str, residue record
        """
        r = {}
        io = cStringIO.StringIO( s )
        line = io.readline().strip()
        while not line:
            line = io.readline().strip()

        r['name'] = line
        io.readline()
        r['code'] = io.readline().split()[0]
        
        atoms = {'serial_number': [], 'name':[], 'amber_type':[],
                 'xyz':[], 'charge':[] }
        for l in self.atomLines( s ):
            items = l.split()
            atoms['serial_number'].append( int( items[0] ) )
            atoms['name'].append( items[1] )
            atoms['amber_type'].append( items[2] )
            atoms['xyz'].append( items[7:10] )
            try:
                atoms['charge'].append( items[10] )
            except:
                pass  ## charge column is not always present
            
        if atoms['charge'] == []:
            atoms['charge'] = self.parseCharges( s )
        
        atoms['charge'] = N.array( atoms['charge'], N.float )
        atoms['xyz']    = N.array( atoms['xyz'], N.float )
        return r, atoms

    
    def createResidue( self, res, atoms ):
        """
        """
        r = AmberResidueType( **res )
        r.letter = M.singleAA( [r.code] )[0]
        r.xyz = atoms['xyz']

        n = len(r.xyz)
        for key in B.PDBModel.PDB_KEYS:
            r[key] = n * ['']
        
        r['type'] = ['ATOM'] * n
        r['residue_name'] = [r.code] * n
        r['residue_number'] = [1] * n
        r['occupancy'] = [1.0] * n
        r['after_ter'] = [0] * n
        r['temperature_factor'] = [0] * n
        
        del atoms['xyz']
        for key, profile in atoms.items():
            r.atoms[key] = profile

        return r

    
    def residueTypes( self ):
        for resblock in self.residueBlocks():
            r, atoms = self.parseResidue( resblock )
            yield self.createResidue( r, atoms )
            

#############
##  TESTING        
#############
import Biskit.test as BT
import glob

class Test(BT.BiskitTest):
    """Test class"""

    def test_amberPrepParser( self ):
        """AmberPrepParser test"""

        files = glob.glob( T.dataRoot()+'/amber/residues/*in')
        files = [ osp.basename( f ) for f in files ]
        results = {}
        if self.local:
            print
        
        for f in files:
            if self.local:
                print 'working on ', f
            self.p = AmberPrepParser( f )
            self.r = [ r for r in self.p.residueTypes() ]
            self.assert_( len(self.r) > 10 )
        
            if self.local:
                print '\tparsed %i residue types from %s' % (len(self.r), f)
            results[ f ] = self.r
        
        self.assertEqual( len(results['all_amino03.in']), 33 )
        
        if self.local:
            for res in results['all_nuc02.in']:
                print res

if __name__ == '__main__':

    BT.localTest(debug=True)

    