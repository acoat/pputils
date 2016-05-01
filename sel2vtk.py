#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2vtk.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Oct 27, 2015
#
# Purpose: Script designed to convert *.slf file to *.vtk. As the old
# slf2vtk.f90 did, it writes a text based file for each time record.
# The script uses pure python to write files, which can be a bit slow
# for large models with many time steps. 
#
# Revised: Dec 17, 2015 
# Made to work on trimmed down version of HRW's selafin_io utilities. But
# selafin_io utilities do not work for python 3.
#
# Revised: Feb 21, 2016
# Use selafin_io_pp utilities, which work under python 2 and 3.
#
# Revised: May 1, 2016
# Now works for 2d and 3d *.slf files
#
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: python sel2vtk.py -i results.slf -o results.vtk
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA

if len(sys.argv) != 5:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python sel2vtk.py -i results.slf -o results.vtk')
	sys.exit()

dummy1 = sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
output_file = sys.argv[4]

# we are going to have one file per time record in the slf file

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# determine if the *.slf file is 2d or 3d by reading how many planes it has
NPLAN = slf.getNPLAN()

# verify that variable ELEVATION or COTE are in the *.slf file 
if (NPLAN > 1):
	el_idx = -1
	for i in range(len(variables)):
		if ((variables[i].find('ELEVATION') > -1)): 
			el_idx = i
		elif ((variables[i].find('COTE Z') > -1)):
			el_idx = i
		#else:
		#	print('Variable ELEVATION not in *.slf file')
		#	print(el_idx)
		#	sys.exit()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# to accomodate code pasting
ikle = IKLE

# to create a list of files
file_out = list()

# initialize the counter
count = 0

# create a list of filenames based on time records in the slf file
filenames = list()
for i in range(len(times)):
	filenames.append(output_file.split('.',1)[0] + "{:0>5d}".format(i) + '.vtk')
	
# to create the multiple output files
for item in filenames:
	file_out.append(item)
	#file_out.append(item)
	file_out[count] = open(item,'w')
	
	# item is the actual file name, which corresponds to each time step
	slf.readVariables(count)
	
	# these are the results for all variables, for time step count
	master_results = slf.getVarValues() 
	
	# vtk header file
	file_out[count].write('# vtk DataFile Version 3.0' + '\n')
	file_out[count].write('Created with pputils' + '\n')
	file_out[count].write('ASCII' + '\n')
	file_out[count].write('' + '\n')
	file_out[count].write('DATASET UNSTRUCTURED_GRID' + '\n')
	file_out[count].write('POINTS ' + str(len(x)) + ' float' + '\n')

	# to write the node coordinates
	for i in range(len(x)):
		if (NPLAN > 1):
			# 3d file
			file_out[count].write(str("{:.3f}".format(x[i])) + ' ' + 
				str("{:.3f}".format(y[i])) + ' ' + 
				str("{:.3f}".format(master_results[el_idx][i])) + '\n')
		else:
			# 2d file
			file_out[count].write(str("{:.3f}".format(x[i])) + ' ' + 
				str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(0.0)) + 
				'\n')
		
	# to write the node connectivity table
	if (NPLAN > 1):
		file_out[count].write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*7) + '\n')
	else:	
		file_out[count].write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4) + '\n')
	
	for i in range(len(ikle)):
		if (NPLAN > 1):
			file_out[count].write('6 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
				str(ikle[i][2]) + ' '+  str(ikle[i][3]) + ' ' + str(ikle[i][4]) + ' ' + 
				str(ikle[i][5]) + '\n')
		else:	
			file_out[count].write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
				str(ikle[i][2]) + '\n')
		
	# to write the cell types
	file_out[count].write('CELL_TYPES ' + str(len(ikle)) + '\n')
	for i in range(len(ikle)):
		if (NPLAN > 1):
			file_out[count].write('13' + '\n')
		else:
			file_out[count].write('5' + '\n')
	
	# write the empty line
	file_out[count].write('' + '\n')

	# write the data
	file_out[count].write('POINT_DATA ' + str(len(x)) + '\n')

	idx_written = list()
	idx_vel_u = -1000
	idx_vel_v = -1000
	idx_vel_z = -1000

	# from the list of variables, find v and u
	for i in range(len(variables)):
		if (NPLAN > 1):
			if (variables[i].find('VELOCITY U') > -1):
				idx_vel_u = i
			elif (variables[i].find('VELOCITY V') > -1):
				idx_vel_v = i
			elif (variables[i].find('VELOCITY W') > -1):
				idx_vel_z = i
		else:
			if (variables[i].find('VELOCITY U') > -1):
				idx_vel_u = i
			elif (variables[i].find('VELOCITY V') > -1):
				idx_vel_v = i
		
		# in case the variables are in french
	for i in range(len(variables)):
		if (NPLAN > 1):
			if (variables[i].find('VITESSE U') > -1):
				idx_vel_u = i
			elif (variables[i].find('VITESSE V') > -1):
				idx_vel_v = i
			elif (variables[i].find('VITESSE W') > -1):
				idx_vel_z = i
		else:
			if (variables[i].find('VITESSE U') > -1):
				idx_vel_u = i
			elif (variables[i].find('VITESSE V') > -1):
				idx_vel_v = i
			
	if ( (idx_vel_u > -1000) and (idx_vel_v > -1000) ):
		# write velocity vectors data 
		file_out[count].write('VECTORS Velocity float' + '\n')
	
		for i in range(len(x)):
			if (NPLAN > 1):
				file_out[count].write(str("{:.4f}".format(master_results[idx_vel_u][i])) + ' ' + 
					str("{:.4f}".format(master_results[idx_vel_v][i])) + ' ' + 
					str("{:.4f}".format(master_results[idx_vel_z][i])) + '\n')				
			else:
				file_out[count].write(str("{:.4f}".format(master_results[idx_vel_u][i])) + ' ' + 
					str("{:.4f}".format(master_results[idx_vel_v][i])) + ' 0.0' + '\n')
			
	# write the rest of the variables
	for i in range(len(variables)):
		#if (i != idx_written[0]) and (i != idx_written[1]):
		file_out[count].write('SCALARS ' + variables[i].replace(' ', '_') + '\n')
		file_out[count].write('float' + '\n')
		file_out[count].write('LOOKUP_TABLE default' + '\n')
		for j in range(len(x)):
			file_out[count].write(str("{:.3f}".format(master_results[i][j])) + '\n')
	
	file_out[count].close()
	count = count + 1
	
