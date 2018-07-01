#
# Module aggregating functions responsible for single region analysis
#

#importing packages for visualization
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#importing packages used in image processing 
from skimage import transform

#importing packages for standard mathematical and data operations
import math
import numpy as np
import os

#constants
from global_variables import DATA_LOCATION_CATALOG

import os

#name of catalog to store brightness profiles
PROFILES_DIRECTORY = '/brightness_profile/'

'''
The function returns boundary points of image region after extending the region in every direction by 
fraction passed in the padding argument

Arguments:
    region - the original region surrounding streak
    padding - float expressing the fraction by which the region is to be extended in each direction

Returns:
    minr, minc, maxr, maxc - integers representing boundary points of extended rectangle surrounding streak

'''
def extend_region_around_streak(region, padding):
    minr, minc, maxr, maxc =  region.bbox


    rmargin = int(padding*(maxr - minr))
    cmargin = int(padding*(maxc - minc))


    minr -= rmargin
    maxr += rmargin
    minc -= cmargin
    maxc += cmargin

    return minr, minc, maxr, maxc
'''
The function takes identified region containing a streak, rotates it so the longer identified axis 
is horizontal and cuts out only the streak

Arguments:
image - the original image
region - a signle labeled region object from skimage

Returns:
newimg - image of the rotated streak 
'''
def cut_out_strk(image, region):
    minr, minc, maxr, maxc = extend_region_around_streak(region, 0.1)

    newimg = image[minr:maxr, minc:maxc]
    newimg = transform.rotate(newimg, -region.orientation*180./math.pi, resize=True)
    
    img_orig_ht = len(newimg)
    strk_ht = region.minor_axis_length

    newimg = newimg[::][int((img_orig_ht-strk_ht)//2):int((img_orig_ht+strk_ht)//2)]
    
    return newimg

'''
This function plots the brightness profile of an identified light streak

Arguments:
  image - the original image
  region - one of regions containing streaks in this image, identified by skimage
  filename - the name of the original image file
  index - ordinal number of the region, indicates how many regions have been already processed for 
  the original image
Returns:
  void
'''
def draw_brightness_profile(image, region, filename, index):
    
    newimg = cut_out_strk(image, region)
    profile = np.sum(newimg, axis=0)
    
    folder_path = DATA_LOCATION_CATALOG + PROFILES_DIRECTORY + filename

    try:
        os.mkdir(DATA_LOCATION_CATALOG + PROFILES_DIRECTORY)
    except:
        pass

   
    try:
        os.mkdir(folder_path)
    except:
        pass
    
    plt.xlabel('Odległość od początku smugi [px]')
    plt.plot(profile)
    plt.savefig(folder_path + "/profile_" + str(index))
    plt.clf()

    return


'''
The function creates image for each streak, containing the angle of rotation
  
Arguments:
  image - the original image
  region - one of regions containing streaks in this image, identified by skimage
  filename - the name of the original image file
  index - ordinal number of the region, indicates how many regions have been already processed for 
  the original image
Returns:
  void
'''
def draw_rotation_angle(image, region, filename, index):

    minr, minc, maxr, maxc = extend_region_around_streak(region, 0.1)
    
    folder_path = DATA_LOCATION_CATALOG + PROFILES_DIRECTORY + filename

    newimg = image[minr:maxr, minc:maxc]

    fig, ax = plt.subplots()
    ax.imshow(newimg)

    direction = np.sign(region.orientation)
    if (direction == 1):
        ystart = maxr-minr
    else:
        ystart = 0

    
    con = mpatches.Arrow(0, ystart, (maxc-minc), direction*(minr-maxr), edgecolor='red', linewidth=2)
    ax.add_artist(con)

    ax.set_axis_off()
    plt.savefig(folder_path + "/reference_" + str(index))
    plt.clf()


