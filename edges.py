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
data_location_catalog = '/home/ula/Dokumenty/Hackathon/obrazy'

#name of output file. The file is created in current location
output_filename = 'analytics.txt'

'''
end of constants
'''

data_location_catalog = data_location_catalog.strip()
data_location_catalog = data_location_catalog.strip(os.sep)

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
    rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='red', linewidth=2)
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
    
    folder_path = os.sep + data_location_catalog + '/light_profile/' + filename

    try:
        os.mkdir(folder_path)
    except:
        pass

    plt.plot(profile)
    plt.savefig(folder_path + "/profile_" + str(index))
    plt.clf()

    return



'''
The function 
'''
def find_and_classify_events(catalog, output_filename):
    no_events = []
    events = []
    #files = os.listdir(catalog)
    streak_length_array = [] #dlugosci smug
    fileCount = {}
    numbFile = {}

    with open(output_filename, 'w') as output:
        for img_filename in glob.glob(catalog+'*.png'):
            tst_img_path = file
            image = io.imread(tst_img_path)
                        
            filename = os.path.basename(img_filename)
            # apply threshold
            thresh = threshold_otsu(image)
            bw = closing(image > thresh/5, square(3))

            # remove artifacts connected to image border
            cleared = clear_border(bw)

            # label image regions
            label_image = label(cleared)
            image_label_overlay = label2rgb(label_image, image=image)

            counter = 0 #ile znalazł rozbłysków alfa
            for region in regionprops(label_image):
                # take regions with large enough areas
                if region.area >= 100:
                    l = region.major_axis_length
                    streak_length_array.append(l)

                    counter+=1
                    numbFile[l] = filename
                    draw_brightness_profile(image, region, filename.replace('.png', ''), counter)
            fileCount[filename] = [counter, 0, 0]#ile znalazlo, ile wyrzuciło po 3 sigma przez długość        
            #print("OK")
            if counter > 0:
                events += [filename]
            else:
                no_events += [filename]

        #numpyLength = np.array(streak_length_array)
        
        lengths_mean = np.mean(streak_length_array)
        outlier_threshold = 3*np.std(streak_length_array) + lengths_mean

        for le in streak_length_array:
            if le < (my_mean / 2):
                fileCount[numbFile[le]][1] += 1
            elif le > (my_mean + threeSigma):
                fileCount[numbFile[le]][2] += 1

        #print (fileCount)
        for f in fileCount:
            #print (fileCount[f])
            output.write(f + " " + str(fileCount[f][0]) + " " + str(fileCount[f][1]) + " " + str(fileCount[f][2])+'\n')
            #lenlength.mean() + 3 * length.std()
    return events, no_events           

events, no_events = find_and_classify_events(data_location_catalog,output_filename)

sort_files(no_events, 'no_events/')





