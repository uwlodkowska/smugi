#importing packages supporting filesystem path walking
import glob

#importing functions from custom modules
from image_processing import find_regions_in_file, process_regions_for_file
from global_variables import DATA_LOCATION_CATALOG
from postprocessing import sort_event_outliers, sort_files

#constants and default values

#name of output file. The file is created in current location
output_filename = 'analytics.txt'


'''
The function iterates over all image files in catalog, identifies streaks and prepares analytics file containing info about event statistics for each file

Arguments:
  catalog - directory to catalog containing images
  output_filename - name of file where the statistics should be saved 

Returns:
  events - list of filenames where streaks have been found
  no_events - list of filenames with no streaks
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
    
    #dict where key - length of streak, value - names of file containing streak of such length
    filename_for_strk_length = {}

    with open(output_filename, 'w') as output:
        for img_filename in glob.glob(catalog+'/*.png'):
           process_regions_for_file(img_filename, streak_length_array, filename_for_strk_length, 
file_stats_dict, events, no_events)                       
        sort_event_outliers(streak_length_array, file_stats_dict, filename_for_strk_length)
	
        output.write("filename | total streaks | short streaks | long streaks\n")

        for f in file_stats_dict:
            output.write(f + " " + str(file_stats_dict[f][0]) + " " + str(file_stats_dict[f][1]) + " " + str(file_stats_dict[f][2])+'\n')
    
    return events, no_events           

events, no_events = find_and_classify_events(DATA_LOCATION_CATALOG, output_filename)

sort_files(no_events, 'no_events/')





