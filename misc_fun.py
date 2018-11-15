# Miscellaneous functions for genetic algorithm to find quickest routes between
# London Underground stations
# v1.0
# Hassan Chagani 2018-11-13
"""
Miscellaneous functions for genetic algorithm to find quickest routes between
London Underground stations.
"""

import datetime
import json
import requests

# Import Station and Route classes
from station_route import Station, Route


def DetermineDate():
    """DetermineDate()
    Calculates date for next Wednesday. Other days can be selected by changing
    the test_day variable if required.
    Returns date in YYYYMMDD format."""

    date_today = datetime.datetime.now().date()
    test_day = 2   # Wednesday = 2; use 0-6 for Monday-Sunday
    # Determine next occurance of day given above
    next_test_day = date_today + datetime.timedelta(days=(test_day - date_today.weekday() + 7) % 7)

    return next_test_day.strftime("%Y%m%d")


def BuildJPlannerURL(from_station_id, to_station_id, time, date):
    """BuildJPlannerURL(from_station_id, to_station_id, time, date)
    Construct string for TfL Journey Planner API to find valid routes between
    two stations.
    Returns URL as string."""

    # Variables to construct URL
    tfl_jp_api_preffix = "https://api.tfl.gov.uk/journey/journeyresults/"
    tfl_jp_api_date = "?date=" + str(date)
    tfl_jp_api_test_time = "&time=" + str(time)
    tfl_jp_api_mode = "&mode=tube"
    tfl_jp_api_walk = "&alternativeWalking=false"

    # Construct URL
    tfl_jp_url = tfl_jp_api_preffix + from_station_id + "/to/" + to_station_id \
                 + tfl_jp_api_date + tfl_jp_api_test_time + tfl_jp_api_mode \
                 + tfl_jp_api_walk

    return tfl_jp_url   # Return URL


def SetJourneyTimes(station_list, journey_time_matrix):
    """SetJourneyTimes(station_list, journey_time_matrix)
    Assigns journey times to Station objects in list from station matrix."""

    # Loop over Station objects in list
    for station in station_list:

        station_idx = station_list.index(station)
        # Assign journey times to Station object
        station.SetTimeTo(station_list, journey_time_matrix[station_idx])


def ContactTfLAPI(tfl_api_url):
    """ContactTfLAPI(tfl_api_url)
    Submits queries to Transport for London (TfL) API.
    Returns dictionary of query results if successful.
    Returns None if unable to acquire data from TfL API."""

    # Make up to 10 attempts to get requested data from TfL API
    attempt = 1
    while attempt < 11:
        try:
            r = requests.get(tfl_api_url)
        # If TfL API cannot be contacted
        except requests.exceptions.ConnectionError:
            print("\nCannot contact TfL API. Please check your internet connection")
            return None

        try:
            tfl_api_data = r.json()
            print("Done.")
            break
        except json.decoder.JSONDecodeError:   # If JSON is missing/invalid
            attempt += 1
            if attempt < 11:
                print("\n\tAttempt no. " + str(attempt), end="...")
            else:
                print("\nError returned from TfL API too many times. Exiting...")
                return None

    return tfl_api_data   # Return query results


def DateTimeConversion(date_time_str):
    """DateTimeConversion(date_time_str)
    Convert datetime strings from TfL journey planner to datetime object.
    Return datetime object."""

    # Datetime strings from TfL journey planner are in YYYY-MM-DDThh:mm:ss
    # format. Replace - and : characters with T, then split string into
    # words separated by T. Finally covert to list of integers and then
    # datetime object.
    date_time_str = date_time_str.replace('-','T')
    date_time_str = date_time_str.replace(':','T')
    date_time_list = date_time_str.split('T')
    date_time_list = list(map(int, date_time_list))
    date_time = datetime.datetime(*date_time_list)

    return date_time   # Return datetime object
