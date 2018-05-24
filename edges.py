#importing packages for visualization
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#importing packages used in image processing 
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb
from skimage import data, io, filters, feature
from skimage import transform

#importing packages for standard mathematical and data operations
import math
import numpy as np

#importing packages supporting filesystem path walking
import os, glob


'''
constants and default values
'''
#path to catalog containing data to process
data_location_catalog = '/home/ula/hackathon/obrazy'

#name of output file. The file is created in current location
output_filename = 'analytics.txt'

#min size of streak to inspect
MIN_STREAK_AREA = 100

#name of catalog to store brightness profiles
PROFILES_DIRECTORY = '/brightness_profile/'

'''
end of constants
'''

data_location_catalog = data_location_catalog.strip()
data_location_catalog = data_location_catalog.strip(os.sep)
data_location_catalog = os.sep + data_location_catalog

'''
This function transfers list of files from catalog containing data to new location.
The list of files is given by the argument files_list, and the new location, with the name given by
folder_name, is a subfolder of the catalog containing data.

Arguments:
  files_list - list of files to move from data catalog
  folder_name - name of the subfolder of the data catalog, where the files from the list should be transferred
Returns:
  void
'''
def sort_files(files_list, folder_name):
    folder_name = folder_name.strip()
    folder_name = folder_name.strip(os.sep)

    folder_path = os.sep + data_location_catalog + os.sep + folder_name
    try:
        os.mkdir(folder_path)
    except:
        pass
    for i in files_list:
        old_path = os.sep + data_location_catalog + os.sep + i
        new_path = folder_path + os.sep + i
        os.rename(old_path, new_path)
    return

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
    minr, minc, maxr, maxc = region.bbox

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
    
    folder_path = data_location_catalog + PROFILES_DIRECTORY + filename

    try:
        os.mkdir(data_location_catalog + PROFILES_DIRECTORY)
    except:
        pass

   
    try:
        os.mkdir(folder_path)
    except:
        pass
    
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

    minr, minc, maxr, maxc = region.bbox
    folder_path = data_location_catalog + PROFILES_DIRECTORY + filename

    try:
        os.mkdir(data_location_catalog + PROFILES_DIRECTORY)
    except:
        pass

   
    try:
        os.mkdir(folder_path)
    except:
        pass

    newimg = image[minr:maxr, minc:maxc]

    fig, ax = plt.subplots()
    ax.imshow(newimg)

    angle = mpatches.Arc((0, 0), (maxc - minc)/4, (maxr - minr)/4, 0, 0, region.orientation*180./math.pi, edgecolor='red', linewidth=2)
    ax.add_patch(angle)

    ax.set_axis_off()
    plt.savefig(folder_path + "/reference_" + str(index))
    plt.clf()

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
  thresh = threshold_otsu(image)
  bw = closing(image > thresh/5, square(3))

  # remove artifacts connected to image border
  cleared = clear_border(bw)

  # label image regions
  labelled_regions = label(cleared)
  return regionprops(labelled_regions)


'''
  The function fills up the data about rejected outlier regions in file_stats_dict

  Arguments:
    streak_length_array - array of streak lengths
    file_stats_dict - dict storing numbers of regions found in each category
    filename_for_strk_length - dict with filenames as values for streak length key

  Returns:
    void
'''
def sort_event_outliers(streak_length_array, file_stats_dict, filename_for_strk_length):
  lengths_mean = np.mean(streak_length_array)
  outlier_threshold = 3*np.std(streak_length_array) + lengths_mean

  for le in streak_length_array:
    if le < (lengths_mean / 2):
      file_stats_dict[filename_for_strk_length[le]][1] += 1
    elif le > (outlier_threshold):
      file_stats_dict[filename_for_strk_length[le]][2] += 1
  #sprawdzić, czy nie trzeba zrobić returna file_stats_dict

'''
The function 
'''
def find_and_classify_events(catalog, output_filename):
    no_events = []
    events = []
    #array storing streak lengths
    streak_length_array = [] 

    #dict where key - original filename, value - array, where the following numbers are stored:
    #at index 0 - total identified regions
    #at index 1 - total of statistically too short streaks
    #at index 2 - total of statistically too long streaks
    file_stats_dict = {}
    
    #dict where key - length of streak, value - name of file containing streak of such length
    filename_for_strk_length = {}

    with open(output_filename, 'w') as output:
        for img_filename in glob.glob(catalog+'/*.png'):
                                  
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

        sort_event_outliers(streak_length_array, file_stats_dict, filename_for_strk_length)

        for f in file_stats_dict:
            output.write(f + " " + str(file_stats_dict[f][0]) + " " + str(file_stats_dict[f][1]) + " " + str(file_stats_dict[f][2])+'\n')
    return events, no_events           

events, no_events = find_and_classify_events(data_location_catalog, output_filename)

sort_files(no_events, 'no_events/')





