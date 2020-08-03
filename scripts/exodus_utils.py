#!/usr/bin/env python3
# coding=utf-8

########################################################################
#                                                                      #
# EXODUS - EPIC XMM-Newton Outburst Detector Ultimate System           #
#                                                                      #
# Rendering for exodus program                                         #
#                                                                      #
# Florent Castellani (2020) - castellani.flo@gmail.com                 #
#                                                                      #
########################################################################
"""
Various functions for EXODUS program
"""

# Third-party imports

import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy import units as u

# Internal imports


########################################################################
#                                                                      #
# Variability computation: procedure count_events                      #
#                                                                      #
########################################################################

def check_correlation(src_1, src_2, corr_tab) :
    """
	Function checking the correlation sources between two source lists
    
	@param  src_1:      The source list of first detector
	@param  src_2:      The source list of second detector
	@param  corr_table: The correlation table

	@return: The correlation table appended
	"""
    
    for i in range(len(src_1)):
        for j in range(len(src_2)):
            c1 = SkyCoord(src_1['RA'][i], src_1['DEC'][i], frame='fk5', unit='deg')
            c2 = SkyCoord(src_2['RA'][j], src_2['DEC'][j], frame='fk5', unit='deg')
            sep = c1.separation(c2)
            if sep.arcsecond < (src_1['R'][i]+src_2['R'][j]):
                corr_tab.add_row([src_1['ID'][i], src_1['INST'][i], src_1['RA'][i], src_1['DEC'][i], src_1['R'][i],\
                                src_2['ID'][j], src_2['INST'][j], src_2['RA'][j], src_2['DEC'][j], src_2['R'][j]])
    
    return corr_tab

########################################################################
    
def check_triple(corr_1, corr_2, corr_3) :
    """
	Function checking correlations between 3 correlation tables
    
	@param  corr_1: The first correlation table
	@param  corr_2: The second correlation table
	@param  corr_3: The third correlation table

	@return: A list with ID and INST of triple correlation sources
	"""
    
    src_cand = []
    triple = []

    for i in range(len(corr_1)):
        src_cand.append([corr_1['ID_1'][i],corr_1['INST_1'][i],corr_1['ID_2'][i],corr_1['INST_2'][i]])
        
    for cand in src_cand:
        t1 = corr_3[np.where((corr_3['ID_1']==cand[0]) & (corr_3['INST_1']==cand[1]))]
        t2 = corr_2[np.where((corr_2['ID_1']==cand[2]) & (corr_2['INST_1']==cand[3]))]
        
    for line1 in t1:
        for line2 in t2:
            if line1['ID_2']==line2['ID_2'] and line1['INST_2']==line2['INST_2']:
                triple.append([line1['ID_1'],line1['INST_1'],line2['ID_1'],line2['INST_1'],line1['ID_2'],line1['INST_2']])
    
    return triple

########################################################################

