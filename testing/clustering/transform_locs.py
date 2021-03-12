######## Script for transforming test points to top view locations ########
#
# Author: Corey Cline
#
# Date: 03/12/2021
# Description:
# Script used to parse incoming json file that contains raw test points from
# camera images using visible markers. Raw locations have been recorded in a
# JSON file. This script will load those test locations, perform top-view
# transform on those locations, and write out the new locations to a new
# JSON file to be used for clustering tests.
#
################################################################################

# Standard library imports
import json
import sys
import os
import logging

# Local imports
sys.path.append("../../utils")
from top_view_transform import *

# Initialize logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Diagnostic display
def diagnostic_display(json_data, indent=0):
    """Prints json data in a clean fashion for debug."""
    print("\t" * indent + "{")
    for key, value in json_data.items():
        print("\t" * indent + "  " + str(key) + ":", end="")
        if isinstance(value, dict):
            print("")
            diagnostic_display(value, indent+1)
        else:
            print(" " * (indent+1) + str(value))
    print("\t" * indent + "}")


    
# Get transform matrix to conduct top view transforms
try: 
    with open("../../config/ground_truth.json") as file:
        truths = json.load(file)
        edge2_s = np.float32(truths["edge2"]["source"])
        edge2_d = np.float32(truths["edge2"]["destination"])
        edge5_s = np.float32(truths["edge5"]["source"])
        edge5_d = np.float32(truths["edge5"]["destination"])

        # Calc transform matrices
        edge2_mat = getTransformMatrix( edge2_s, edge2_d )
        edge5_mat = getTransformMatrix( edge5_s, edge5_d )

        # Aggregate in dict for use in loop
        mats = {"edge2" : edge2_mat,
                "edge5" : edge5_mat }
        
# Catch exceptions
except Exception as error:
    logging.error( "Error collecting ground truth data." )
    print( error )
    exit(1)

# Open test points file and begin parsing
try:
    with open("test_points_raw.json", "r") as file:
        raw_data = json.load(file)
        print(f"RAW DATA: \n=================={raw_data}")
        diagnostic_display(raw_data)
        new_data = {}
        
        # Iterate for each test
        for test in raw_data:
            new_data[test] = {}
            # Iterate for edge2 and edge5 in each test
            for edge in raw_data[test]:
                new_data[test][edge] = []
                # Iterate for each test point in edge2/edge5
                for point in raw_data[test][edge]:
                    # Transform location with correct transform matrix
                    new_point = transformCentroidLocation(point,mats[edge])
                    # Add transformed point to new_data
                    new_data[test][edge].append(new_point)

    # Display new locations
    print("NEW DATA: \n===================")
    diagnostic_display(new_data)
                    
    # Write new locations out to file
    with open("test_points_topview.json", "w") as file:
        json.dump(new_data, file)
        
# Catch if file not found
except FileNotFoundError as fnfe:
    logging.error(fnfe)
    logging.error("File not found.")    

finally:
    logging.info("DONE")
 
