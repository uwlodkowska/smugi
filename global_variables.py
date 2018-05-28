#
# module aggregating global variables
#

#importing packages supporting filesystem path walking
import os

#path to catalog containing data to process
DATA_LOCATION_CATALOG = '/home/ula/hackathon/obrazy'
DATA_LOCATION_CATALOG = DATA_LOCATION_CATALOG.strip()
DATA_LOCATION_CATALOG = DATA_LOCATION_CATALOG.strip(os.sep)
DATA_LOCATION_CATALOG = os.sep + DATA_LOCATION_CATALOG
