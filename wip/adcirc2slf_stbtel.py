#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2slf_stbtel.py                  # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 26, 2015
#
# Purpose: Script takes in a mesh in ADCIRC format, and converts it to
# TELEMAC's slf file using stbtel. The same is achieved by using 
# converter.py, which for some reason wouldn't work for me.
#
# Note that if coordinates are in UTM, stbtel seems to allow F9.1, which
# means that some precision is lost in the coordinates!
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python adcirc2slf_stbtel.py -i out.grd -o out.slf
# where:
# -i input adcirc mesh file
# -o output *.slf file generated by stbtel (automatically writes *.cli file)
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import subprocess
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 5 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python adcirc2slf_stbtel.py -i out.grd -o out.slf'
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 = sys.argv[3]
slf_file = sys.argv[4]
cli_file = slf_file.split('.',1)[0] + '.cli'

# create a stbtel cas file for the adcirc2slf converstion
fout = open('adcirc2slf.cas',"w")
fout.write('UNIVERSAL FILE = \'' + str(adcirc_file) + '\'' + '\n')
fout.write('GEOMETRY FILE FOR TELEMAC = \'' + str(slf_file) + '\'' + '\n')
fout.write('BOUNDARY CONDITIONS FILE = \'' + str(cli_file) + '\'' + '\n')
fout.write('ELIMINATION OF BACKWARD DEPENDENCIES = NO' + '\n')
fout.write('MESH GENERATOR = ADCIRC' + '\n')

fout.close()
print curdir
print 'Operating system: ' + os.name

if (os.name == 'posix'):

	# change the directory to python27 folder of the local telemac installation
	os.chdir('/home/pprodano/opentelemac/v7p0r1/scripts/python27')

	# pass the SYSTELCFG system variable
	subprocess.call('export SYSTELCFG=/home/pprodano/opentelemac/v7p0r1/configs/systel.cis-debian.cfg', shell=True)
	
	# runs the stbtel
	cmd_str = 'python runcode.py stbtel -s ' + curdir + '/adcirc2slf.cas'
	subprocess.call(cmd_str, shell=True)
	
	# changes the current dir to pputils default
	os.chdir(curdir)
	
	# deletes the stbtel compiled executable
	os.remove('stbtel')
