# This takes a fits image, rebins into factors of the original to save space, and then makes 3D object for printing
#  Nothing is done in parallel, and there are undoubtably other inifficiencies, misspellings, and code run amok

import yt  # this assumes yt is installed, but really, we only use it as a fits reader, so it can be replaced with pyfits or somesuch
import numpy as np
import matplotlib.pyplot as plt
from utils import bin_ndarray

# image of sun in xrays in 1024x1024 (full disk)
# intensity = the z
ffile = '/Users/jillnaiman/Dropbox/tactileSun/comp_XRT20161006_061228.4.fits'

# height of final cube? (w/rt original image x/y pixels)
cube_height = 128


# rebin factor
rebin_shape = np.array([4,4,4]) # factors of origional
#rebin_shape = np.array([16,16,16]) # factors of origional


# where to save the obj and mtl files?
fileout = '/Users/jillnaiman/Dropbox/tactileSun/sunout'


# plot the surface?  Just if you wanna debug
plot_surf = False


#--------------------------------------------------------------------------

# load fits
ds = yt.load(ffile)
dd = ds.all_data()
intensity = dd[('fits', 'image_0')]

# fixing zeros
intensity[intensity < 0] = 0.0
intensity = np.log10(intensity)
intensity[np.isnan(intensity)] = 0.0
intensity[np.isneginf(intensity)] = 0.0

x = (dd[('fits', 'x')].v).astype('int')
y = (dd[('fits', 'y')].v).astype('int')

# remap into 1024 x 1024 image, make pixels intensity
intensity_xy = np.zeros([x.max(),y.max()])
for c in xrange(len(x)):
    intensity_xy[x[c]-1,y[c]-1] = intensity[c]

# regrid
rebin_shape[0] = (x.max()/rebin_shape[0])
rebin_shape[1] = (y.max()/rebin_shape[1])
rebin_shape[2] = (cube_height*1.0/rebin_shape[2])

intensity_xy = bin_ndarray(intensity_xy, (rebin_shape[0],rebin_shape[1]), operation='mean')

intensity_xy = ( (intensity_xy-intensity_xy.min())/intensity_xy.ptp()*rebin_shape[2] ).astype('int')


# little boarder - needed for the marching cubes to behave nicely
lb = 1

# fill grid with 1s
grid = np.ones([ rebin_shape[0]+2*lb,rebin_shape[1]+2*lb,rebin_shape[2]+2*lb ])

# now, carve out zeros where the shape of the intensity "image" is in 3D
for i in xrange(rebin_shape[0]):
    for j in xrange(rebin_shape[1]):
        grid[i+lb,j+lb,lb:intensity_xy[i,j]-1+lb] = 0.0

        
# do the marching cubes on this object to get surface where object == 0
from skimage import measure # pip install scikit-image to use this
verts, faces, normals, values = measure.marching_cubes(grid, 0.0)#, spacing=(1.0,1.0,1.0))

if plot_surf: # plot if we are debugging
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(verts[:, 0], verts[:,1], faces, verts[:, 2],
                    cmap='Reds', lw=1)
    plt.show()


# was gonna add color to the surface for prettiness, but didn't get around to it
#import matplotlib.cm as cm
#cmap = cm.get_cmap('Reds') # red color map, default 0->1

# do we need vt and vn? ... not if no texture or colors... for now...
# if so, I think we can use normals and values from marching cube algorhtym
y = []

# first, write a little intro the image object
y.append('#\n')
y.append('# object Sun' + '\n')
y.append('#\n')

# now, output a copy of the file
# now loop add verticies
for i in range(0, len(verts)):
    y.append('v ' + str(verts[i,0]) + ' ' + str(verts[i,1]) + ' ' + str(verts[i,2]) + '\n')

for i in xrange(len(faces)):
    y.append('f ' + str(faces[i,0]+1) + ' ' + str(faces[i,1]+1) + ' ' + str(faces[i,2]+1) + '\n')

# write the OBJ file
import os
f = open(fileout+'.obj', 'w')
for i in range(0,len(y)):
    f.write(y[i].replace('\r\n', os.linesep))

f.close()
