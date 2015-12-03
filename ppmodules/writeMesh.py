#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy             as np             # numpy
import scipy.io          as io             # scipy's io functions for loadmat()
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeAdcirc(n,e,x,y,z,ikle,name):
	#{{{
	# write the file output
	# name argument is the name of the output adcirc file
	fout = open(name, 'w')
	
	# now to write the adcirc mesh file
	fout.write("ADCIRC" + "\n")
	# writes the number of elements and number of nodes in the header file
	fout.write(str(e) + " " + str(n) + "\n")
	
	# writes the nodes
	for i in range(n):
		fout.write(str(i+1) + " " + str("{:.3f}".format(x[i] )) + " " + 
			str("{:.3f}".format(y[i])) + " " + str("{:.3f}".format(z[i])) + "\n")
	
	# writes the elements
	# the readAdcirc function assigns the ikle starting at zero, so that is why
	# we have to add 1
	for i in range(e):
		fout.write(str(i+1) + " 3 " + str(ikle[i,0]+1) + " " + str(ikle[i,1]+1) + 
			" " + 	str(ikle[i,2]+1) + "\n")

	# close the fout file
	fout.close()
	#}}}
	return None
#
def writeVTKscalar(n,e,x,y,z,ikle,fname,vname):
	#{{{
	# write the file output
	# fname argument is the name of the output adcirc file
	fout = open(fname, 'w')
	
	# vname is the variable name of the scalar variable
	
	# vtk header file
	fout.write('# vtk DataFile Version 3.0' + '\n')
	fout.write('Created with pputils' + '\n')
	fout.write('ASCII' + '\n')
	fout.write('' + '\n')
	fout.write('DATASET UNSTRUCTURED_GRID' + '\n')
	fout.write('POINTS ' + str(len(x)) + ' float' + '\n')
	
	# to write the node coordinates
	for i in range(len(x)):
		fout.write(str("{:.3f}".format(x[i])) + ' ' + 
			str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(0.0)) + 
			'\n')
			
	# to write the node connectivity table
	fout.write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4) + '\n')
	
	for i in range(len(ikle)):
		fout.write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
			str(ikle[i][2]) + '\n')
			
	# to write the cell types
	fout.write('CELL_TYPES ' + str(len(ikle)) + '\n')
	for i in range(len(ikle)):
		fout.write('5' + '\n')
		
	# write the empty line
	fout.write('' + '\n')
	
	# write the data
	fout.write('POINT_DATA ' + str(len(x)) + '\n')
	
	# write the z as scalar data also
	fout.write('SCALARS ' + vname + '\n')
	fout.write('float' + '\n')
	fout.write('LOOKUP_TABLE default' + '\n')
	for i in range(len(x)):
		fout.write(str("{:.3f}".format(z[i])) + '\n')

	fout.close()
	#}}}
	return None
	
def writeVTKswan(adcirc_file, mat_file, vtk_file):
	#{{{
	# writes the master *.vtk file
	
	# TODO: finish this method when non-stationary unstructured swan
	# results become available ...
	
	
	#}}}
	return None

