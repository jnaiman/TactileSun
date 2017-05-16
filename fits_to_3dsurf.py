# This takes a fits image, rebins into factors of the original to save space, and then makes 3D object for printing
#  Nothing is done in parallel, and there are undoubtably other inifficiencies, misspellings, and code run amok

# also, assumes yt is installed, but this is only used as a fits reader, so this can be replaced
# also need: 'pip install scikit-image' to use this

import numpy as np

# image of sun in xrays in 1024x1024 (full disk)
# intensity = the z
ffile = '/Users/jillnaiman1/Dropbox/tactileSun/comp_XRT20161006_061228.4.fits'

# height of final cube? (w/rt original image x/y pixels)
cube_height = 128


# rebin factor
rebin_shape = np.array([4,4,4]) # factors of origional

# also, if we've done filtering, we might have a lot of zeros
#  what is the minimum "zero" level for filtering?
# 1 means 1 voxel of final resolution
zero_voxel = 4



# where to save the obj and mtl files?
fileout = '/Users/jillnaiman1/Dropbox/tactileSun/sunout_process1'


# plot the surface?  Just if you wanna debug
plot_surf = False


#--------------------------------------------------------------------------
from tactilesun.processImages import load_image, local_histogram_equalization
from tactilesun.fitsTo3dSurf import convert_image_to_obj as co

# load the image
xs,ys,scidata = load_image(ffile)

# apply processing
newimg = local_histogram_equalization(scidata, 'rank_eq')

# output processed 3d thingy
co(newimg, fileout, rebin_shape, cube_height, zero_voxel)
#co(ffile, fileout, rebin_shape, cube_height, zero_voxel)
