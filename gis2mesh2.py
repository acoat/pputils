#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 gis2mesh2.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: February 2, 2017
#
# Purpose: Same as the gis2mesh.py script, except that this version refines
# the original mesh based on a tin. A function is needed to convert the
# elevations in the tin to a custom area constraint in the originally created
# mesh. Triangle is then executed with the -r option (refine), which then
# creates a mesh that is refined based on the values in the tin.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python gis2mesh.py -n nodes.csv -b boundary.csv -l lines.csv -h none -a area.csv -f function.csv -t tin.grd -o mesh.grd
#
# where:
# --> -n is the file listing of all nodes (incl. embedded nodes
#                  if any). The nodes file consist of x,y,z or x,y,z,size;
#                  The size parameter is an optional input, and is used 
#                  by gmsh as an extra parameter that forces element 
#                  size around a particular node. For triangle, it has
#                  no meaning. The nodes file must be comma separated, and
#                  have no header lines. 
#
# --> -b is the node listing of the outer boundary for the mesh.
#                  The boundary file is generated by snapping lines
#                  to the nodes from the nodes.csv file. The boundary file 
#                  consists of shapeid,x,y of all the lines in the file.
#                  Boundary has to be a closed shape, where first and last 
#                  nodes are identical. Shapeid is a integer, where the
#                  boundary is defined with a distict id (i.e., shapeid 
#                  of 0). 
#
# --> -l is the node listing of the constraint lines for the mesh.
#                  The lines file can include open or closed polylines.
#                  The file listing has shapeid,x,y, where x,y have to 
#                  reasonable match that of the nodes.csv file. Each distinct
#                  line has to have an individual (integer) shapeid. If no 
#                  constraint lines in the mesh, enter 'none' without the
#                  quotes.
#
# --> -h is the listing of the holes in the mesh. The holes file is
#                  generated by placing a single node marker inside a
#                  closed line constraint. The holes file must include a 
#                  x,y coordinate within the hole boundary. If no holes
#                  (islands) in the mesh, enter 'none' without the quotes. 
#                  Note that for triangle, the format of the holes file 
#                  is different than for gmsh!!!
#
# --> -a is the listing of the area constraints in the mesh. The area file is
#                  generated by placing a single node marker inside a
#                  closed line constraint. The areas file must include a 
#                  x,y,area for each area bounded by each area. 
#
# --> -f is the function that converts the interpolated tin values to an
#                  area constraint that will be used by Triangle in the mesh
#                  refinement procedure. The file is to contain x and y
#                  coordinates of a table lookup function.
#
# --> -t is the tin file that is used in the refinement procedure that
#                  interpolates an elevation to a centroid of each element in
#                  the originally generated mesh by Triangle. The interpolated
#                  elevation is then converted (via a tranfer function) to an
#                  area constraint. Triangle is then called again with the
#                  refinement option (-r) that refines the originally created
#                  mesh based on the area constraints from the tin model.
#
#--> -o is the output adcirc file that is the quality mesh.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys,shutil                       # system parameters
import numpy             as np             # numpy
from collections import OrderedDict        # for removal of duplicate nodes
import struct                              # to determine sys architecture
import subprocess                          # to execute binaries
from ppmodules.readMesh import *           # to get all readMesh functions
import matplotlib.tri    as mtri           # matplotlib triangulations
#
#
# determine which version of python the user is running
if (sys.version_info > (3, 0)):
  version = 3
  pystr = 'python3'
elif (sys.version_info > (2, 7)):
  version = 2
  pystr = 'python'
#
if len(sys.argv) == 17 :
  nodes_file = sys.argv[2]
  boundary_file = sys.argv[4]
  lines_file = sys.argv[6]
  holes_file = sys.argv[8]
  areas_file = sys.argv[10]
  function_file = sys.argv[12]
  tin_file = sys.argv[14]
  output_file = sys.argv[16]
else:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python gis2mesh.py -n nodes.csv -b boundary.csv -l lines.csv -h holes.csv -a areas.csv -f function.csv -t tin.grd -o mesh.grd')
  sys.exit()

# the code between ##### is exactly the same as that in gis2mesh.py
# ###################################################################
# to determine if the system is 32 or 64 bit
archtype = struct.calcsize("P") * 8

# call gis2triangle.py
print('Generating Triangle input files ...')
subprocess.call([pystr, 'gis2triangle.py', '-n', nodes_file, 
  '-b', boundary_file, '-l', lines_file, '-h', holes_file, 
  '-o', 'mesh.poly'])

# read areas file
areas_data = np.loadtxt(areas_file, delimiter=',',skiprows=0,unpack=True)

# this is the number of area constraints to add
# find out how many area points are in the area file
num_areas = len(open(areas_file).readlines())
  
# this is not optimal, but rather than changing the gis2triangle_kd.py
# script, read the mesh.poly file, and append the information on the 
# area constraints before running Triangle. This is sloppy, but it works!

with open('mesh.poly', 'a') as f: # 'a' here is for append to the file
  f.write('\n')
  f.write(str(num_areas) + '\n')
  
  # if more than one area constraint node
  if (num_areas == 1):
    f.write('1' + ' ' + str(areas_data[0]) + ' ' +\
        str(areas_data[1]) + ' ' + str(0) + ' ' +\
        str(areas_data[2]) + '\n')
  else:
    for i in range(num_areas):
      f.write(str(i+1) + ' ' + str(areas_data[0,i]) + ' ' +\
        str(areas_data[1,i]) + ' ' + str(0) + ' ' +\
        str(areas_data[2,i]) + '\n')

# now run Triangle (to generate initial mesh)
print('#############################################################')
print(' Triangle is generating initial mesh ...')
print('#############################################################')

if (os.name == 'posix'):
  # this assumes chmod +x has already been applied to the binaries
  if (archtype == 32):
    subprocess.call( ['./triangle/bin/triangle_32', '-Dqa', 'mesh.poly' ] )
  else:
    subprocess.call( ['./triangle/bin/triangle_64', '-Dqa', 'mesh.poly' ] )
elif (os.name == 'nt'):
  subprocess.call( ['.\\triangle\\bin\\triangle_32.exe', '-Dqa', 'mesh.poly' ] )
else:
  print('OS not supported!')
  print('Exiting!')
  sys.exit()

# at this point, Triangle has generated mesh.1.poly, mesh.1.node, mesh1.ele

# now call triangle2adcirc.py and create mesh_temp.grd file
print('Converting Triangle output to ADCIRC mesh format ...')
subprocess.call([pystr, 'triangle2adcirc.py', '-n', 'mesh.1.node',
                 '-e', 'mesh.1.ele', '-o', 'mesh_initial.grd'])

# construct the wkt file of the initial mesh
wkt_file_initial = 'mesh_initialWKT.csv'

# now convert the *.grd file to a *.wkt file by calling adcirc2wkt.py
# this is the first cut mesh
print('Converting ADCIRC mesh to WKT format ...')
subprocess.call([pystr, 'adcirc2wkt.py', '-i', 'mesh_initial.grd', 
                 '-o', wkt_file_initial])

# ###################################################################

# read the mesh_initial.grd file, and extract from it the centroid coordinate
# for each element
n,e,x,y,z,ikle = readAdcirc('mesh_initial.grd')

# create centroids for each element in mesh_initial.grd
centroid_x = np.zeros(e)
centroid_y = np.zeros(e)

for i in range(e):
  centroid_x[i] = (x[ikle[i,0]] +x[ikle[i,1]] + \
    x[ikle[i,2]]) / 3.0  
  centroid_y[i] = (y[ikle[i,0]] +y[ikle[i,1]] + \
    y[ikle[i,2]]) / 3.0 

# read the tin file
print('Reading TIN ...')
t_n,t_e,t_x,t_y,t_z,t_ikle = readAdcirc(tin_file)

# now interpolate centroid_x and centroid_y from the tin.grd
# create tin triangulation object using matplotlib
tin = mtri.Triangulation(t_x, t_y, t_ikle)

# to perform the triangulation
interpolator = mtri.LinearTriInterpolator(tin, t_z)
centroid_z = interpolator(centroid_x, centroid_y)

# now we need a transfer function to translate the centroid_z values
# to an equivalent min area constraint for Triangle to use in its refinement
# procedure

# read in the transfer function using numpy arrays
function_data = np.loadtxt(function_file, delimiter=',',skiprows=0,unpack=True)

# first column is the x value --> coresponds to values of the tin
fx = function_data[0,:]

# second column is the y value --> coresponds to values of max area constraint
fy = function_data[1,:]

# use numpy to interpolate the area constraints using the function as a table lookup
centroid_a = np.interp(centroid_z,fx,fy)

# to generate a series array containting the elements in the mesh.1.ele
e_count = np.arange(1,e+1)

# now write the area constraint for the refinement
aout = open('mesh.1.area', 'w')
aout.write(str(e) + '\n')
for i in range(e):
  aout.write(str(i+1) + '  ' + str(centroid_a[i]) + '\n')
aout.write('')
aout.close()

print('#############################################################')
print(' Triangle is generating refined mesh ...')
print('#############################################################')

# now run Triangle (to generate the refined mesh)
if (os.name == 'posix'):
  # this assumes chmod +x has already been applied to the binaries
  if (archtype == 32):
    subprocess.call( ['./triangle/bin/triangle_32', '-rDpqa', 'mesh.1'])
  else:
    subprocess.call( ['./triangle/bin/triangle_64', '-rDpqa', 'mesh.1'])
elif (os.name == 'nt'):
  subprocess.call( ['.\\triangle\\bin\\triangle_32.exe', '-rDpqa', 'mesh.1'])
else:
  print('OS not supported!')
  print('Exiting!')
  sys.exit()

# now call triangle2adcirc.py and create mesh_final.grd file
print('Converting Triangle output to ADCIRC mesh format ...')
subprocess.call([pystr, 'triangle2adcirc.py', '-n', 'mesh.2.node',
                 '-e', 'mesh.2.ele', '-o', 'mesh_final.grd'])

# construct the output wkt file
wkt_file_final = 'mesh_finalWKT.csv'

# now convert the *.grd file to a *.wkt file by calling adcirc2wkt.py
print('Converting final ADCIRC mesh to WKT format ...')
subprocess.call([pystr, 'adcirc2wkt.py', '-i', 'mesh_final.grd',
                 '-o', wkt_file_final])

# copies the 'mesh_final.grd' to the actual output name from the command line
shutil.copyfile('mesh_final.grd', output_file)

print('Removing temporary files ...')
os.remove('mesh.poly')

os.remove('mesh.1.poly')
os.remove('mesh.1.node')
os.remove('mesh.1.ele')
os.remove('mesh.1.area')

os.remove('mesh.2.poly')
os.remove('mesh.2.node')
os.remove('mesh.2.ele')




