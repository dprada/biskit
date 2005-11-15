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

## Contributions: olivier PERIN
##
## last $Author$
## last $Date$
## $Revision$

import Biskit.tools as tools
from Biskit.PDBModel import PDBModel
from Biskit.Mod.Benchmark import Benchmark
from Biskit.Mod.ValidationSetup import ValidationSetup as VS
from Biskit.Mod.CheckIdentities import Check_Identities as CI
from Biskit.Mod.Modeller import Modeller

import os
from string import *
import re
import Numeric as N


class Analyse:
    """
    Create a folder named analyse in the project root folder
    that contains the following results:

    GLOBAL: global rmsd: all atoms, c-alpha only, percentage of
    identities, Modeller score, and the number of templates

    LOCAL: results of the cross validation, rmsd per residue c-alpha
    only for each templates and the mean rmsd

    3D structure: pickle down the final.pdb that is the best model of
    the project and the mean rmsd is set inside (temperature_factor)
    """

    F_RESULT_FOLDER = '/analyse'
    F_TEMPLATE_FOLDER = VS.F_RESULT_FOLDER

    F_PDBModels = Benchmark.F_PDBModels_OUT
    F_MODELS = Modeller.F_RESULT_FOLDER + Modeller.F_PDBModels

    F_INPUT_ALNS= '/t_coffee/final.pir_aln'

    F_INPUT_RMSD = Benchmark.F_RESULT_FOLDER
    F_RMSD_AA = Benchmark.F_RMSD_AA
    F_RMSD_CA = Benchmark.F_RMSD_CA


    F_OUTPUT_VALUES = F_RESULT_FOLDER + '/global_results.out'
    F_CROSS_VAL = F_RESULT_FOLDER + '/local_results.out'
    F_FINAL_PDB = F_RESULT_FOLDER + '/final.pdb'

    def __init__( self, outFolder, log=None ):
        """
        log      - LogFile instance or None, None reports to STDOUT
        """
        self.outFolder = tools.absfile( outFolder )
        self.log = log

        self.prepareFolders()


    def prepareFolders( self ):
        """
        Create folders needed by this class.
        """
        if not os.path.exists( self.outFolder + self.F_RESULT_FOLDER ):
            os.mkdir( self.outFolder + self.F_RESULT_FOLDER )


    def parseFile( self, name ):
        """
        Parse a identity matrix file
        -> list of lists
        """
        f = open( name, 'r')
        result = []
        lines = f.readlines()
        
        for l in lines:
            if not l[0] == '#':
                r =[]
                for s in l.split():
                    try:
                        r += [float(s)]
                    except:
                        pass
                if len(r)>=1:
                    result += [ r ]
                
        f.close()
        return result
            

######################################################################
####  GLOBAL RESTULTS: RMSD_AA, RMSD_CA,
####                   %ID(mean of the templates),
####                   Nb of Templates 

    def global_rmsd_aa(self, input_folder = None, validation_folder= None):
        """
        -> rmsd_aa_wo_if: list [], global all atom rmsd for each
              template without iterative fitting
        -> rmsd_aa_if: list [], global all atom rmsd for each
              templates with iterative fitting
        """
        input_folder = input_folder or self.F_INPUT_RMSD
        validation_folder = validation_folder or self.outFolder + \
                            self.F_TEMPLATE_FOLDER

        folders = os.listdir(validation_folder)

        rmsd_aa_wo_if = {}
        rmsd_aa_if = {}
        
        for folder in folders:

            file = "%s/%s"%(validation_folder, folder + self.F_RMSD_AA)
            lst = self.parseFile( file )
            
            rmsd_aa_wo_if[folder] = [ lst[0][0] ]
            rmsd_aa_if[folder]    = [ lst[0][1], lst[0][2]*100.]

        return rmsd_aa_wo_if, rmsd_aa_if


    def global_rmsd_ca(self, input_folder = None, validation_folder= None):
        """
        -> rmsd_ca_wo_if: list [], global CA rmsd for each template
              without iterative fitting
        -> rmsd_ca_if: list [], global CA rmsd for each template
              with iterative fitting
        """
        input_folder = input_folder or self.F_INPUT_RMSD
        validation_folder = validation_folder or self.outFolder + \
                            self.F_TEMPLATE_FOLDER

        folders = os.listdir(validation_folder)

        rmsd_ca_wo_if = {}
        rmsd_ca_if = {}
        
        for folder in folders:

            file = "%s/%s"%(validation_folder, folder + self.F_RMSD_CA)
            
            lst = self.parseFile( file )

            rmsd_ca_wo_if[folder] = [ lst[0][0] ]
            rmsd_ca_if[folder]    = [ lst[0][1], lst[0][2]*100.]
        
        return rmsd_ca_wo_if, rmsd_ca_if
    

    def get_identities(self, nb_templates, validation_folder = None):
        """
        Calculate the mean of the percentage of identities for each
        template with the others.
        nb_templates - int, number of templates used in the cross-validation
        -> identities: dic {}, mean %ID for each template
        """

        validation_folder = validation_folder or self.outFolder + \
                            self.F_TEMPLATE_FOLDER

        folders = os.listdir(validation_folder)
        identities = {}

        for folder in folders:
            file = "%s/%s"%(validation_folder, folder + \
                            CI.F_OUTPUT_IDENTITIES_COV)
            
            lst = self.parseFile( file )
            
            ## identity to mean template
            identities[folder] = N.sum(lst[0][1:])/nb_templates
            
        return identities


    def get_score(self, input_folder = None, validation_folder = None):
        """
        Get the best global modeller score for each template re-modeled
        -> score: dic {}, modeller score for each template
        """
        input_folder = input_folder or Modeller.F_RESULT_FOLDER
        validation_folder = validation_folder or self.outFolder + \
                            self.F_TEMPLATE_FOLDER

        folders = os.listdir(validation_folder)
        score = {}

        for folder in folders:
            file = "%s/%s"%(validation_folder, folder + Modeller.F_SCORE_OUT)
           
            file = open(file, 'r')
            string_lines = file.readlines()[3]
            score[folder] = float( split(string_lines)[1] )

        return score
    
    
    def output_values(self, rmsd_aa_wo_if, rmsd_aa_if,  rmsd_ca_wo_if,
                      rmsd_ca_if, identities, score, nb_templates,
                      output_file = None):

        output_file = output_file or self.outFolder + self.F_OUTPUT_VALUES

        file = open( output_file, 'w' )
        file.write("PROPERTIES OF RE-MODELED TEMPLATES:\n\n")
        file.write("     | NORMAL FIT  |          ITERATIVE FIT          | IDENTITY  | SCORE | NR\n"  )
        file.write("PDB  | heavy  CA   | heavy percent    CA   percent   | mean to   | mod8  | of\n")
        file.write("code | rmsd   rmsd | rmsd  discarded  rmsd discarded | templates |       | templates\n")

        for key, value in rmsd_aa_wo_if.items():

            file.write("%4s %6.2f %6.2f %6.2f %8.1f %7.2f %7.1f %10.1f %9i %6i\n"%\
                       (key, value[0], rmsd_ca_wo_if[key][0], rmsd_aa_if[key][0],
                        rmsd_aa_if[key][1], rmsd_ca_if[key][0], rmsd_ca_if[key][1],
                        identities[key], score[key], nb_templates))

        file.close()


########################################################################
#########  LOCAL RESULTS: Cross Validation ---- RMSD / Res  

    def get_aln_info(self, output_folder = None):
        """
        -> aln_dictionary {}, contains information from the alignment
        between the target and its templates
        """
        output_folder = output_folder or self.outFolder

        ci = CI(outFolder=output_folder)
        
        string_lines = ci.get_lines()
        aln_length = ci.search_length(string_lines)
        aln_dictionnary = ci.get_aln_sequences(string_lines, aln_length)
        aln_dictionnary = ci.get_aln_templates(string_lines, aln_dictionnary,
                                               aln_length)
        aln_dictionnary = ci.identities(aln_dictionnary)
        
        return aln_dictionnary
    

    def get_templates_rmsd(self, templates):
        """
        templates - list [string], name of the different templates
        -> template_rmsd_dic {}, contains all the rmsd per residues
            of all the templates
        """
        template_rmsd_dic = {}
        for template in templates:
            
            pdb_list = self.outFolder + self.F_TEMPLATE_FOLDER \
                       + "/%s"%template + self.F_PDBModels
                
            pdb_list = tools.Load(pdb_list)
            
            template_rmsd_dic[template] = pdb_list[0].compress(pdb_list[0].maskCA()).aProfiles["rmsd2ref_if"]
                
        return template_rmsd_dic


    def templates_profiles(self, templates, aln_dic, template_rmsd_dic):
        """
        templates - list [string], name of the different templates
        aln_dic   - dic {}, contains all the informations between the
                       target and its templates from the alignment
        template_rmsd_dic - {}, contains all the rmsd per residues of all
                            the templates
        -> template_profiles: dic {}, contains all the profile rmsd of
            each template with the target and their %ID
        """
        templates_profiles = {}

        target_aln = aln_dic["target"]["seq"]
        for template in templates:
            template_aln = []
            template_profile = []
            template_info = {}

            template_rmsd = template_rmsd_dic[template]
            for key in aln_dic:
                if(key[:4] == template):
                    template_aln = aln_dic[key]["seq"]
                    
            no_res = -1
            for i in range(len(target_aln)):
                if(template_aln[i] is not '-'):
                    no_res += 1

                if(target_aln[i] != '-' and template_aln[i] != '-'):
                    template_profile.append(template_rmsd[no_res])
                    
                if(target_aln[i] != '-' and template_aln[i] == '-'):
                    template_profile.append(-1)
                    
            template_info["rProfile"] = template_profile
            
            for key in aln_dic["target"]["cov_ID"]:
                if(key[:4] == template):
                    template_info["cov_ID"] = \
                                      aln_dic["target"]["cov_ID"][key]

            templates_profiles[template] = template_info

        return templates_profiles

        

    def output_cross_val(self, aln_dic, templates_profiles,
                         templates, model, output_file=None):
        """
        """
        output_file = output_file or self.outFolder + self.F_CROSS_VAL

        mean, sum, values = 0, 0, 0
        mean_rmsd = []
        
        for k,v in aln_dic["target"]["cov_ID"].items():
            
            if (k != "target"):
                sum += aln_dic["target"]["cov_ID"][k]
                values +=1
        
        cov_id_target = float(sum/values)

        for i in range(len(templates_profiles[templates[0]]["rProfile"])):

            mean = 0
            sum = 0
            n_values = 0
             
            for k in templates_profiles:

                if(templates_profiles[k]["rProfile"][i] != -1):
                    sum +=  templates_profiles[k]["rProfile"][i]
                    n_values += 1
            
            if(n_values != 0):        
                mean = float(sum) / float(n_values)

            else: mean = -1

            mean_rmsd.append(mean)

        ## write header
        file = open (output_file, 'w')
        file.write("Mean rmsd of model to templates and the residue rmsd.\n")
        
        ## write pdb code
        file.write(" "*7)
        for k in templates_profiles.keys():
            file.write("%6s"%k)
        file.write("  mean\n")

        ## write mean rmsd
        file.write(" "*7)
        for k in templates_profiles.keys():
            file.write("%6.2f"%templates_profiles[k]["cov_ID"])
        file.write("\n%s\n"%('='*70))

        ## write rmsd residue profiles
        resDic = model.compress( model.maskCA()).atoms
        for i in range(len(templates_profiles[templates[0]]["rProfile"])):
            file.write("%3i %3s"%(resDic[i]['residue_number'],
                                  resDic[i]['residue_name']))
            for k in templates_profiles:
                file.write("%6.2f"%(templates_profiles[k]["rProfile"][i]))
                
            file.write("%6.2f\n"%(mean_rmsd[i]))
            
        file.close()

        return mean_rmsd


#################################################
######   3D Structure: mean RMSD  


    def updatePDBs_charge(self, mean_rmsd_atoms, model):
        """
        pickle down the final.pdb which is judged to be the best model
        of the project. The mean rmsd to the templates is written to the
        temperature_factor column.
        
        mean_rmsd_atoms - list[int], mean rmsd for each atom of the
        target's model
        model - PDBModel, target's model with the highest modeller score
        """
        for a,v in zip(model.atoms, mean_rmsd_atoms):
            a['temperature_factor'] = v
    
        model.writePdb(self.outFolder + self.F_FINAL_PDB)       
            


######################
### LAUNCH FUNCTION ##
######################
    
    def go(self, output_folder = None, template_folder = None):
        
        ##
        pdb_list = tools.Load(self.outFolder + self.F_MODELS)
        model = PDBModel(pdb_list[0])
        
        ## 
        output_folder = output_folder or self.outFolder + self.F_RESULT_FOLDER
        template_folder = template_folder or self.outFolder +VS.F_RESULT_FOLDER
        
        templates = os.listdir(template_folder)

        ##
        global_rmsd_aa_wo_if, global_rmsd_aa_if = self.global_rmsd_aa()
        global_rmsd_ca_wo_if, global_rmsd_ca_if = self.global_rmsd_ca()
        nb_templates = len(templates)-1
        
        identities = self.get_identities(nb_templates)
        score = self.get_score()
        
        self.output_values(global_rmsd_aa_wo_if, global_rmsd_aa_if,
                           global_rmsd_ca_wo_if, global_rmsd_ca_if,
                           identities, score, nb_templates)

        ##
        aln_dic = self.get_aln_info(output_folder=self.outFolder)

        template_rmsd_dic = self.get_templates_rmsd(templates)
        templates_profiles = self.templates_profiles(templates,
                                                     aln_dic,
                                                     template_rmsd_dic)
        mean_rmsd = self.output_cross_val(aln_dic, templates_profiles,
                                          templates, model)
        
        ##
        mean_rmsd_atoms = model.res2atomProfile(mean_rmsd) 
        self.updatePDBs_charge(mean_rmsd_atoms, model)



############
## MAIN
############

if __name__ == '__main__':

    #base_folder = tools.testRoot() + '/Mod/project'

    base_folder = tools.absfile('~/Test')
    a = Analyse(outFolder = base_folder)
    a.go()

    
 ##    folders = os.listdir(tools.absfile('~/Homstrad_final/'))


##     for folder in folders:
        
##         base_folder = tools.absfile('~/Homstrad_final/%s'%folder)

##         a = Analyse(outFolder = base_folder)
        
##         a.go()
    
