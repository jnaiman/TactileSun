from astropy.io import fits

#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as plt
#from matplotlib import cm
#from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

from scipy import fftpack
#import pylab as py
import pyfits
#Download radialProfile from http://www.astrobetter.com/wiki/python_radial_profiles
#import radialProfile


from skimage import data
from skimage.util.dtype import dtype_range
from skimage.util import img_as_ubyte
from skimage import exposure
from skimage.morphology import disk
from skimage.filters import rank
#import matplotlib



use_yt = False

if use_yt:
    import yt


# load up image based on what loading package we wanna use
def load_image(fits_file,
               data_name = ('fits','image_0'),
               xfits = ('fits','x'), yfits = ('fits','y'), plot_surf=False):

    # load fits
    if use_yt:
        ds = yt.load(fits_file)
        dd = ds.all_data()
        scidata = dd[data_name]
        
        #x = (dd[xfits].v).astype('int')
        #y = (dd[yfits].v).astype('int')
        xscale = 1.0
        yscale = 1.0
    else:
        hdulist = fits.open(fits_file)
        xscale = hdulist[0].header['XSCALE']
        yscale = hdulist[0].header['YSCALE']
        scidata = hdulist[0].data

    return xscale, yscale, scidata


# take 1d and 2d power spectrum
def take_fft(scidata):

    image = (scidata-np.mean(scidata))/np.max(scidata)

    F1 = fftpack.fft2(image)

    # Now shift the quadrants around so that low spatial frequencies are in
    # the center of the 2D fourier transformed image.
    F2 = fftpack.fftshift(F1)
 
    # Calculate a 2D power spectrum
    psd2D = np.abs(F2)**2
 
    # Calculate the azimuthally averaged 1D power spectrum
    #psd1D = radialProfile.azimuthalAverage(psd2D)

    return psd2D



def local_histogram_equalization(scidata, type_eq, disknum=30):

    #img = scidata
    img = (scidata-np.mean(scidata))/np.max(scidata)
    #img = img_as_ubyte(data.moon())

    #img_rescale = exposure.equalize_hist(img)


    # Global equalize
    if type_eq == 'rescale':
        return exposure.equalize_hist(img)
    # Equalization
    elif type_eq == 'rank_eq':
        selem = disk(disknum)
        img_eq = rank.equalize(img, selem=selem)
        # flip dark and light
        img_eq = 255 - img_eq
        return img_eq
        
