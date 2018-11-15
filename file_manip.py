# File and file name manipulation functions for genetic algorithm to find
# quickest routes between London Underground stations.
# v1.0
# Hassan Chagani 2018-11-13
"""
File and file name manipulation functions for genetic algorithm to find
quickest routes between London Underground stations.
"""

import datetime
import glob
import json
import numpy as np
import os
import pandas as pd
import requests

# Import Station and Route classes
from station_route import Station, Route
# Import miscellaneous functions
import misc_fun as MFun


def FindFile(directory, suffix, n_files=1):
    """FindFile(directory, suffix, n_files=1)
    Finds files with suffix in directory.
    Returns latest file if n_files=1.
    Returns list of files if n_files!=1.
    Returns None if unsuccessful."""

    # List of files in directory with suffix
    list_of_files = glob.glob("./" + directory + "/*." + suffix)

    try:   # Find latest file
        latest_file = max(list_of_files, key=os.path.getctime)

        if n_files == 1:   # Return latest file
            return latest_file

        else:   # Return list of all files
            return list_of_files

    except ValueError:   # If no files with suffix exist in directory
        return None


def SelectFileFromList(list_of_files):
    """SelectFileFromList(list_of_files)
    Presents list of filenames to user and asks which to select.
    Returns selected filename."""

    while True:
        # Present user with list of filenames
        for idx, f in enumerate(list_of_files):
            print("[" + str(idx) + "]\t" + f)
        u_input = input("Please select file: ")

        try:
            f = list_of_files[int(u_input)]
            if int(u_input) < 0:   # Demand positive integer only
                raise IndexError
            break

        except IndexError:   # Negative integer or out of range 
            print("Invalid choice. Please try again.")
        except ValueError:   # String or float entered
            print("Invalid choice. Please try again.")

    return f   # Return selected filename


def CreateStationList(filename):
    """CreateStationList(filename)
    Creates list of Station objects from list of station names in file.
    Returns list of Station objects if successful.
    Return None if unsuccessful."""

    # Read station names from file
    with open(filename) as f:
        data = f.readlines()

    # If file contains < 3 stations, output error message
    if len(data) < 3:
        print("File must contain more than 2 stations.")
        return None

    # Preffix and suffix for Transport for London (TfL) API
    tfl_stopPoints_api_preffix = "https://api.tfl.gov.uk/StopPoint/Search/"
    tfl_stopPoints_api_suffix = "?modes=tube"
    station_list = []   # Initialise empty station list

    print("Station names from station file:")

    # Loop over all stations
    for line in data:
        station_name = line.strip()
        print(station_name, end='...')
        station_name_url = station_name.replace(' ', '%20')   # Name for URL

        # Get station data from TfL API
        tfl_api_url = tfl_stopPoints_api_preffix + station_name_url +\
                      tfl_stopPoints_api_suffix
        station_data = MFun.ContactTfLAPI(tfl_api_url)
        if station_data == None:
            return None

        # In the case of any ambiguity with station names, give user possible
        # stations to choose
        if station_data['total'] > 1:
            print(station_name + " returned several results:")
            while True:
                for station in range(station_data['total']):
                    # Only list those stations with an ID number
                    if 'icsId' in station_data['matches'][station].keys():
                        print("[" + str(station) + "]", end='\t')
                        print(station_data['matches'][station]['name'])
                u_input = input("Please select station: ")
                try:
                    station_id = station_data['matches'][int(u_input)]['icsId']
                    if int(u_input) < 0:   # Demand positive integer only
                        raise IndexError
                    station_name = station_data['matches'][int(u_input)]['name']
                    break
                except IndexError:   # Negative integer or out of range
                    print("Invalid choice. Please try again.")
                except KeyError:   # icsId key does not exist
                    print("Invalid choice. Please try again.")
                except TypeError:   # Float or string entered
                    print("Invalid choice. Please try again.")

        # Otherwise, if no ambiguity with station name take first entry
        else:
            try:
                station_id = station_data['matches'][0]['icsId']
            except IndexError:   # If no entry, station doesn't exist
                print("Station " + station_name + " does not exist.", end=' ')
                print("Please edit list and re-run.")
                return None

        # Create new Station object and append to station list
        station_list.append(Station(station_name, station_id))

    return station_list   # Return list of Station objects


def CreateStationMatrix(station_list, time, date):
    """CreateStationMatrix(station_list, time, date)
    Create matrix of journey times between stations by submitting queries to
    Transport for London (TfL) API, and calculating mean journey times from
    results. Assumes that journey time matrix is hollow (diagonal elements are
    all zero) and symmetric (journey times from Station A and Station B are the
    same as those from Station B to Station A). Therefore, builds half the
    matrix, then adds it to its transpose. Matrix is then written out to csv
    file for future use and relative journey times are assigned to Station
    objects.
    Returns 0 if successful.
    Returns None if unable to acquire journey planner data from TfL API."""

    journey_time_matrix = []   # Initialise matrix of journey times
    print("Calculating journey times...")

    # Loop over Station objects in station_list
    for start_station in station_list[:-1]:
        print("From " + start_station.name)

        # It is reasonable to assume matrix is symmetric, i.e. journey times
        # from A to B are same as those from B to A. Therefore, only need to
        # fill half the matrix, then add it to its transpose. This will result
        # in a hollow matrix whose diagonal elements are all zero.
        # start_station as rows
        # end_station as columns
        start_station_idx = station_list.index(start_station)
        # For now, fill elements in diagonal and to its left with zeros.
        journey_durations = [0.0 for station in station_list[:start_station_idx+1]]

        # Loop over Station objects starting from Station object after
        # start_station in station_list to find journey times
        for end_station in station_list[start_station_idx+1:]:
            print("\tto " + end_station.name, end='...')

            # Get journey planner data from TfL API
            tfl_jp_url = MFun.BuildJPlannerURL(start_station.id_no,\
                                               end_station.id_no, time, date)
            journey_data = MFun.ContactTfLAPI(tfl_jp_url)
            if journey_data == None:
                return None

            # Number of journeys returned by TfL API
            n_journeys = len(journey_data['journeys'])

            # Calculate mean journey time in minutes and round to nearest integer
            mean_duration = 0.0
            for journey in range(n_journeys):

                mean_duration += float(journey_data['journeys'][journey]['duration'])\
                                 / float(n_journeys)

            journey_durations.append(round(mean_duration))

        # Build journey time matrix layer-by-layer
        # (i.e. start_station-by-start_station)
        journey_time_matrix.append(journey_durations)

    # All elements in final row of journey time matrix should be zero for final
    # start_station (which has no end_station)
    journey_time_matrix.append([0.0 for station in station_list])
    # Convert to numpy array to exploit matrix manipulation methods
    journey_time_matrix = np.array(journey_time_matrix)
    # Add journey time matrix to its transpose to obtain hollow, symmetric
    # matrix
    journey_time_matrix += journey_time_matrix.T

    # Assign relative journey times to Station objects using values in matrix
    MFun.SetJourneyTimes(station_list, journey_time_matrix)

    # Write matrix to csv file for future use. Index and columns of pandas
    # dataframe set to start station names and end station IDs respectively.
    station_matrix = pd.DataFrame(journey_time_matrix)
    station_matrix.index = [station.name for station in station_list]
    station_matrix.columns = [station.id_no for station in station_list]
    # Write matrix to file in ./station_matrices/ directory
    station_matrix.to_csv("./station_matrices/" + date + '_' + time + '_'\
                          + str(station_matrix.index.size)\
                          + "stationMatrix.csv")

    return 0   # No errors


def ReadStationMatrix(filename):
    """ReadStationMatrix(filename)
    Reads station matrix file and creates list of Station objects from station
    names (index column) and IDs (column headings) from csv file.
    Returns list of Station objects.
    """

    # Index column = station names
    # Column headings = station IDs
    station_matrix = pd.read_csv(filename, index_col=0)

    station_list = []

    print("Station names read from station matrix file:")

    # Loop over all stations names and IDs in matrix to create Station objects
    for station in range(station_matrix.index.size):

        station_list.append(Station(station_matrix.index[station],\
                                    station_matrix.columns[station]))
        print(station_list[station])

    # Assign relative journey times to Station objects using values in matrix
    MFun.SetJourneyTimes(station_list, station_matrix.values)

    return station_list   # Return list of Station objects


def StationMatrixTimeAndDate(filename):
    """StationMatrixTimeAndDate(filename)
    Extract time and date information from station matrix file name. The time
    and date refer to those values inputted into the TfL journey planner to
    generate the station matrix file using the CreateStationMatrix() function.
    Returns time and date."""

    # Format of filename is ./station_matrices/YYYYMMDD_hhmm_*stationMatrix.csv
    # So replace / with _: ._station_matrices_YYYYMMDD_hhmm_*stationMatrix.csv
    # Then split string to get list of words to extract time and date
    words = filename.replace('/', '_').split('_')
    time, date = words[4], words[3]

    return time, date   # Return time and date
