import numpy as np
#import matplotlib.pyplot as plt
from utils import bin_ndarray


use_yt = False
if use_yt: import yt  # this assumes yt is installed, but really, we only use it as a fits reader, so it can be replaced with pyfits or somesuch



# can take in an image or directory path
def convert_image_to_obj(fits_file, obj_file_out, rebin_shape, cube_height, zero_voxel,
                         data_name = ('fits','image_0'),
                         xfits = ('fits','x'), yfits = ('fits','y'), plot_surf=False):

    fileout = obj_file_out
    ffile = fits_file

    # check if we are being given a fits file or an image
    if type(fits_file) == str:

        if use_yt:
            # load fits
            ds = yt.load(ffile)
            dd = ds.all_data()
            intensity = dd[data_name]
            x = (dd[xfits].v).astype('int')
            y = (dd[yfits].v).astype('int')
            # fixing zeros
            intensity[intensity < 0] = 0.0
            intensity = np.log10(intensity)
            intensity[np.isnan(intensity)] = 0.0
            intensity[np.isneginf(intensity)] = 0.0
            intensity_xy = np.zeros([x.max(),y.max()])
            # remap into 1024 x 1024 image, make pixels intensity
            for c in xrange(len(x)):
                intensity_xy[x[c]-1,y[c]-1] = intensity[c]

    else:
        x = np.linspace(1,fits_file.shape[0], fits_file.shape[0], dtype=int)
        y = np.linspace(1,fits_file.shape[1], fits_file.shape[1], dtype=int)
        intensity = fits_file
        # fixing zeros
        intensity[intensity < 0] = 0.0
        intensity = np.log10(intensity)
        intensity[np.isnan(intensity)] = 0.0
        intensity[np.isneginf(intensity)] = 0.0
        intensity_xy = intensity




    # regrid
    rebin_shape_in = np.zeros(3)
    rebin_shape_in[0] = (x.max()/rebin_shape[0])
    rebin_shape_in[1] = (y.max()/rebin_shape[1])
    rebin_shape_in[2] = (cube_height*1.0/rebin_shape[2])

    rebin_shape_in = rebin_shape_in.astype('int')

    intensity_xy = bin_ndarray(intensity_xy, (rebin_shape_in[0],rebin_shape_in[1]), operation='mean')

    intensity_xy = ( (intensity_xy-intensity_xy.min())/intensity_xy.ptp()*rebin_shape_in[2] ).astype('int')

    intensity_xy[intensity_xy == 0] = zero_voxel
    
    # little boarder - needed for the marching cubes to behave nicely
    lb = 1

    # fill grid with 1s
    #print(grid)
    grid = np.ones([ rebin_shape_in[0]+2*lb,rebin_shape_in[1]+2*lb,rebin_shape_in[2]+2*lb ])

    #print(grid.shape)

    # now, carve out zeros where the shape of the intensity "image" is in 3D
    for i in xrange(rebin_shape_in[0]):
        for j in xrange(rebin_shape_in[1]):
            grid[i+lb,j+lb,lb:intensity_xy[i,j]-1+lb] = 0.0


    # do the marching cubes on this object to get surface where object == 0
    from skimage import measure # pip install scikit-image to use this

    #print(grid)
    
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
