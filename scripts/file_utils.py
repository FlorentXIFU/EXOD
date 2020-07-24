#!/usr/bin/env python3
# coding=utf-8

########################################################################
#                                                                      #
# EXOD - EPIC-pn XMM-Newton Outburst Detector                          # #                                                                      #
# Various utilities for both detector and renderer                     #
#                                                                      #
# Inés Pastor Marazuela (2019) - ines.pastor.marazuela@gmail.com       #
#                                                                      #
########################################################################
"""
Various resources for both detector and renderer
"""

# Built-in imports

import sys
import os
import time
from functools import partial
import subprocess

# Third-party imports

from math import *
from astropy.table import Table
from astropy import wcs
from astropy.io import fits
import numpy as np
import scipy.ndimage as nd
import skimage.transform

# Internal imports

import file_names as FileNames


########################################################################
#                                                                      #
# Function and procedures                                              #
#                                                                      #
########################################################################


def open_files(folder_name) :
    """
    Function opening files and writing their legend.
    @param  folder_name:  The directory to create the files.
    @return: log_file, info_file, variability_file, counter_per_tw,
    detected_variable_areas_file, time_windows_file
    """

    # Fixing the name of the folder
    if folder_name[-1] != "/" :
        folder_name += "/"

    # Creating the folder if needed
    if not os.path.exists(folder_name):
        try :
            os.makedirs(folder_name)
        except :
            print("Error in creating output directory.\nABORTING", file=sys.stderr)
            exit(-1)

    # Declaring the files
    log_file = None
    var_file = None
    reg_file = None

    # Creating the log file
    try:
        log_file = open(folder_name + FileNames.LOG, 'w+')

    except IOError as e:
        print("Error in creating log.txt.\nABORTING", file=sys.stderr)
        print(e, file=sys.stderr)
        close_files(log_file, var_file, reg_file)
        print_help()
        exit(-1)

    # Creating the file to store variability per pixel
    try :
        var_file = folder_name + FileNames.VARIABILITY

    except IOError as e:
        print("Error in creating {0}.\nABORTING".format(FileNames.VARIABILITY), file=sys.stderr)
        print(e, file=sys.stderr)
        close_files(log_file, var_file, reg_file)
        print_help()
        exit(-1)

    # Creating the region file to store the position of variable sources
    try :
        reg_file = folder_name + FileNames.REGION

    except IOError as e:
        print("Error in creating {0}.\nABORTING".format(FileNames.REGION), file=sys.stderr)
        print(e, file=sys.stderr)
        close_files(log_file, var_file, reg_file)
        print_help()
        exit(-1)

    return log_file, var_file, reg_file


########################################################################


def close_files(log_f, reg_f) :
    """
    Function closing all files.
    """

    if log_f :
        log_f.close()

    if reg_f :
        reg_f.close()

########################################################################

class Tee(object):
    """
    Class object that will print the output to the log_f file
    and to terminal
    """
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # If you want the output to be visible immediately
    def flush(self) :
        pass

########################################################################


def read_from_file(file_path, counter=False, comment_token='#', separator=';') :
    """
    Function returning the content
    @param counter: True if it is the counters that are loaded, False if it is the variability
    @return: A list
    """
    data = []
    i = 0
    nb_lignes = -1

    with open(file_path) as f:
        for line in f:
            #if len(line) > 2 and comment_token not in line :
            if comment_token not in line :
                if i % 200 == 0 :
                    data.append([])
                    nb_lignes += 1
                if not counter :
                    data[nb_lignes].append(float(line))
                else :
                    data[nb_lignes].append([float(tok) for tok in line.split(separator)])
                i += 1

    return data


########################################################################


def read_tws_from_file(file_path, comment_token='#', separator=';') :
    """
    Reads the list of time windows from its file.
    @return: A list of couples (ID of the TW, t0 of the TW)
    """
    tws = []

    with open(file_path) as f :
        for line in f :
            if len(line) > 2 and comment_token not in line :
                line_toks = line.split(separator)
                tws.append((int(line_toks[0]), float(line_toks[1])))

    return tws

########################################################################

class Source(object):
    """
    Datastructure providing easy storage for detected sources.\n

    Attributes:\n
    id_src:  The identifier number of the source\n
    inst:    The type of CCD\n
    ccd:     The CCD where the source was detected at\n
    rawx:    The x coordinate on the CCD\n
    rawy:    The y coordinate on the CCD\n
    r:       The radius of the variable area\n
    x:       The x coordinate on the output image\n
    y:       The y coordinate on the output image
    """

    def __init__(self, src):
        """
        Constructor for Source class. Computes the x and y attributes.
        @param src : source, output of variable_sources_position
            id_src:  The identifier number of the source
            inst:    The type of CCD
            ccd:     The CCD where the source was detected at
            rawx:    The x coordinate on the CCD
            rawy:    The y coordinate on the CCD
            r:       The raw pixel radius of the detected variable area
        """
        super(Source, self).__init__()

        self.id_src = src[0]
        self.inst = src[1]
        self.ccd = src[2]
        self.rawx = src[3]
        self.rawy = src[4]
        self.rawr = src[5]
        self.x = None
        self.y = None
        self.skyr = self.rawr * 64
        self.ra = None
        self.dec = None
        self.r = self.skyr * 0.05 # arcseconds


    def sky_coord(self, path, img, log_f) :
        """
        Calculate sky coordinates with the sas task edet2sky.
        Return x, y, ra, dec
        """

        # Launching SAS commands, writing to output file
        out_file = path + 'variable_sources.txt'
        # The out_file will be temporarily written to the output directory, then removed.

        if self.id_src == 0 : s = '>'
        else :      s = '>>'

        command = f"""
        export SAS_ODF={path};
        export SAS_CCF={path}ccf.cif;
        export HEADAS={FileNames.HEADAS};
        . $HEADAS/headas-init.sh;
        . {FileNames.SAS};
        echo "# Variable source {self.id_src}"; #{s} {out_file};
        edet2sky datastyle=user inputunit=raw X={self.rawx} Y={self.rawy} ccd={self.ccd} calinfoset={img} -V 0 {s} {out_file}
        """

        # Running command, writing to file
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        #log_f.write('\n * Source position *\n')
        log_f.write(" * Variable source {0} * ".format(self.id_src))
        time.sleep(0.5)
        with open(out_file) as f:
            for line in f:
                print(line)
                log_f.write(line)

        # Reading
        det2sky = np.array([line.rstrip('\n') for line in open(out_file, 'r')])

        for i in range(len(det2sky)) :
            # Equatorial coordinates
            self.ra, self.dec = det2sky[np.where(det2sky == '# RA (deg)   DEC (deg)')[0][0] + 1].split()

            # Sky pixel coordinates
            self.x, self.y    = det2sky[np.where(det2sky == '# Sky X        Y pixel')[0][0] + 1].split()

        # Removing temporary output file
        os.remove(out_file)

########################################################################


def read_sources_from_file(file_path, comment_token='#', separator=';') :
    """
    Reads the source from their file
    @return: A list of Source objects
    """

    sources = []

    with open(file_path) as f :
        for line in f :
            if len(line) > 2 and comment_token not in line :
                toks = line.split(separator)
                sources.append(Source(toks[0], int(toks[1]), float(toks[2]), float(toks[3]), float(toks[4])))

    return sources

########################################################################

def PN_config(data_matrix) :
    """
    Arranges the variability data for EPIC_PN
    """
    data_v = []

    # XMM-Newton EPIC-pn CCD arrangement
    ccds = [[8,7,6,9,10,11],[5,4,3,0,1,2]]

    # Building data matrix
    for c in ccds[0] :
        data_v.extend(np.flipud(data_matrix[c]))
    i = 0
    for c in ccds[1] :
        m = np.flip(data_matrix[c])
        for j in range(64) :
            data_v[i] = np.append(data_v[i], m[63 - j])
            i += 1
    return data_v

########################################################################

def M1_config(data_matrix) :
    """
    Arranges the variability data for EPIC_MOS_1
    """
    corner = np.zeros((300,600))
    
    # First part
    data_1 = np.concatenate((corner,data_matrix[1].T,np.flip(data_matrix[6].T),corner), axis=0)
    
    # Second part
    data_2 = np.concatenate((data_matrix[2].T,np.flipud(data_matrix[0]),np.flip(data_matrix[5].T)), axis=0)
    
    # Third part
    data_3 = np.concatenate((corner,data_matrix[3].T,np.flip(data_matrix[4].T),corner), axis=0)

    # Building data matrix
    data_v = np.rot90(np.concatenate((data_1, data_2, data_3), axis=1))
        
    return data_v

########################################################################

def M2_config(data_matrix) :
    """
    Arranges the variability data for EPIC_MOS_2
    """
    corner = np.zeros((300,600))
    
    # First part
    data_1 = np.concatenate((corner,data_matrix[1].T,np.flip(data_matrix[6].T),corner), axis=0)
    
    # Second part
    data_2 = np.concatenate((data_matrix[2].T,np.flipud(data_matrix[0]),np.flip(data_matrix[5].T)), axis=0)
    
    # Third part
    data_3 = np.concatenate((corner,data_matrix[3].T,np.flip(data_matrix[4].T),corner), axis=0)

    # Building data matrix
    data_v = np.flip(np.concatenate((data_1, data_2, data_3), axis=1))
        
    return data_v

########################################################################
#                                                                      #
# Geometrical transformations                                          #
#                                                                      #
########################################################################

def data_transformation_PN(data, header) :
    """
    Performing geometrical transformations from raw coordinates to sky coordinates
    @param data: variability matrix
    @param header: header of the clean events file
    flip@return: transformed variability data
    """

    # Header information
    angle = header['PA_PNT']

    xproj = [float(header['TDMIN6']), float(header['TDMAX6'])] # projected x limits
    yproj = [float(header['TDMIN7']), float(header['TDMAX7'])] # projected y limits
    xlims = [float(header['TLMIN6']), float(header['TLMAX6'])] # legal x limits
    ylims = [float(header['TLMIN7']), float(header['TLMAX7'])] # legal y limits

    # scaling factor
    sx = 648 / (xlims[1] - xlims[0])
    sy = 648 / (ylims[1] - ylims[0])
    # pads (padding)
    padX = (int((xproj[0] - xlims[0])*sx), int((xlims[1] - xproj[1])*sx))
    padY = (int((yproj[0] - ylims[0])*sy), int((ylims[1] - yproj[1])*sy))
    # shape (resizing)
    pixX = 648 - (padX[0] + padX[1])
    pixY = 648 - (padY[0] +padY[1])

    # Transformations
    ## Rotation
    dataR = np.flipud(nd.rotate(data, angle, reshape = True))
    ## Resizing
    dataT = skimage.transform.resize(dataR, (pixY, pixX), mode='constant', cval=0.0) # xy reversed
    ## Padding
    dataP = np.pad(dataT, (padY, padX), 'constant', constant_values=0) # xy reversed

    return dataP

########################################################################

def data_transformation_MOS(data, header) :
    """
    Performing geometrical transformations from raw coordinates to sky coordinates
    @param data: variability matrix
    @param header: header of the clean events file
    flip@return: transformed variability data
    """

    # Header information
    angle = header['PA_PNT']

    xproj = [float(header['TDMIN6']), float(header['TDMAX6'])] # projected x limits
    yproj = [float(header['TDMIN7']), float(header['TDMAX7'])] # projected y limits
    xlims = [float(header['TLMIN6']), float(header['TLMAX6'])] # legal x limits
    ylims = [float(header['TLMIN7']), float(header['TLMAX7'])] # legal y limits

    # scaling factor
    sx = 648 / (xlims[1] - xlims[0])
    sy = 648 / (ylims[1] - ylims[0])
    
    
    # pads (padding)
    interX = (int((xproj[0] - xlims[0])*sx), int((xlims[1] - xproj[1])*sx))
    interY = (int((yproj[0] - ylims[0])*sy), int((ylims[1] - yproj[1])*sy))
    
    padX = (int(interX[0]/(interX[0] + interX[1])*148), 148-int(interX[0]/(interX[0] + interX[1])*148))
    padY = (int(interY[0]/(interY[0] + interY[1])*148), 148-int(interY[0]/(interY[0] + interY[1])*148))

    # Transformations
    ## Rotation
    dataR = np.flipud(nd.rotate(data, angle, reshape = False))
    ## Resizing
    dataT = skimage.transform.resize(dataR, (500, 500), mode='constant', cval=0.0)
    ## Padding
    dataP = np.pad(dataT, (padY, padX), 'constant', constant_values=0) # xy reversed

    return dataP
