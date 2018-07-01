#
# A module with functions dealing with postprocessing of streak search - sorting results and creating output files
#

#importing packages for standard mathematical and data operations
import numpy as np

#importing packages supporting filesystem path walking
import os

#importing from custom modules
from global_variables import DATA_LOCATION_CATALOG

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

    folder_path = DATA_LOCATION_CATALOG + os.sep + folder_name
    try:
        os.mkdir(folder_path)
    except:
        pass
    for i in files_list:
        old_path = DATA_LOCATION_CATALOG + os.sep + i
        new_path = folder_path + os.sep + i
        os.rename(old_path, new_path)
    return

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



