#
# Module aggregating functions responsible for identifying and processing region for each image
#

import numpy as np

#importing packages used in image processing 
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square, opening
from skimage.color import label2rgb
from skimage import data, io, filters, feature


#importing packages supporting filesystem path walking
import os

#importing functions from custom modules
from region_processing import draw_brightness_profile, draw_rotation_angle
from global_variables import DATA_LOCATION_CATALOG

#constants

#min size of streak to inspect
MIN_STREAK_AREA = 100



'''
   The function finds region containing streaks for imgage

   Arguments:
     img-filename - string containing filename to inspect

   Returns:
     list of RegionProperties objects 
'''
def find_regions_in_file(img_filename):
  image = io.imread(img_filename)
  # apply threshold
  #thresh = threshold_otsu(image)

  flat_image = np.ndarray.flatten(image)

  sorted_flat = np.sort(np.unique(flat_image))

  thresh = sorted_flat[-1]*0.085

  bw = closing(image > thresh, square(3))

  # remove artifacts connected to image border
  cleared = clear_border(bw)

  # label image regions
  labelled_regions = label(cleared)
  return regionprops(labelled_regions)


'''

The function does all region processing for single image from catalog: it iterates over each found region containing streak
and updates global statistics. It also adds the filename to correct array, so it can be processed according to whether there
have been any events in this file

Arguments:
  img_filename - the name of image filename
  streak_length_array - array of streak lengths that have been found
  filename_for_strk_length - dict of filenames for streak lengths
  file_stats_dict - doct of statistics of regions for each filename
  events - array of filenames with identified events
  no_events - array of filenames, for which no events have been found
Returns:
  void

'''
def process_regions_for_file(img_filename, streak_length_array, filename_for_strk_length, file_stats_dict, events, no_events):
  image = io.imread(img_filename)
  filename = os.path.basename(img_filename)     
  regions_found = find_regions_in_file(img_filename)
  counter = 0 
  for region in regions_found:
    #only take regions with large enough areas
    if region.area >= MIN_STREAK_AREA:
      l = region.major_axis_length
      streak_length_array.append(l)
      counter += 1
      filename_for_strk_length[l] = filename
      draw_brightness_profile(image, region, filename.replace('.png', ''), counter)
      draw_rotation_angle(image, region, filename.replace('.png', ''), counter)

      file_stats_dict[filename] = [counter, 0, 0]        
            
  if counter > 0:
    events += [filename]
  else:
    no_events += [filename]
