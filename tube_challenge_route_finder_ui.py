# User interface functions for genetic algorithm to find quickest routes
# between London Underground stations.
# v1.0
# Hassan Chagani 2018-11-13
"""
User interface functions for genetic algorithm to find quickest routes between
London Underground stations.
"""

import datetime
import os
import random
import re

# Import genetic algorithm functions
import gen_alg_LUstations as Galus
# Import file manipulation functions
import file_manip as FMan
# Import DetermineDate from miscellaneous functions
from misc_fun import DetermineDate
# Import visualisation and statistics functions
import vis_stat_fun as VSFun


def GeneticAlgorithmMenu():
    """GeneticAlgorithmMenu()
    Presents user with default parameters for genetic algorithm and asks
    whether they any should be changed. Random seed is also chosen here but not
    set.
    Returns following parameters for genetic algorithm as tuple:
        Number of generations;
        Number of routes per generation;
        Number of elite routes to pass down to next generation;
        Mutation rate;
        Random seed.
    Returns None if user wishes to exit program."""

    # Set default parameters
    n_generations = 100   # Number of generations to simulate
    pop_size = 100   # Number of routes per generation
    elite_size = 10   # Number of elite routes to pass down to next generation
    mutation_rate = 0.01

    # Assign random seed
    random_bytes = os.urandom(8)
    random_seed = int.from_bytes(random_bytes, byteorder='big')

    while True:
        # Present current parameters to user and ask for changes or acceptance
        print("\n")
        print("----------------------------")
        print("Genetic Algorithm Parameters")
        print("----------------------------")
        print("[0]\t Number of generations: " + str(n_generations))
        print("[1]\t Number of routes per generation: " + str(pop_size))
        print("[2]\t Number of elite routes to pass down to next generation: " + str(elite_size))
        print("[3]\t Mutation rate: " + str(mutation_rate))
        print("[4]\t Random seed: " + str(random_seed))
        print("[5]\t Accept parameters")
        u_input = input("Please select a parameter to change or accept all parameters (q to quit): ")

        try:
            value = int(u_input)

            if value == 0:   # Change number of generations
                u_second_input = input("Please enter number of generations: ")
                try:
                    second_value = int(u_second_input)
                    if second_value <= 0:   # Demand positive integer only
                        raise ValueError
                    n_generations = second_value
                except ValueError:   # Negative integer, 0, string or float entered
                    print("Invalid number. Please enter an integer > 0.")
                continue

            elif value == 1:   # Change number of routes per generation
                u_second_input = input("Please enter number of routes per generation: ")
                try:
                    second_value = int(u_second_input)
                    # Demand positive integer > number of elite routes
                    # Demand integer != 1 if elite_size = 0
                    if second_value < elite_size or (second_value == 1 and elite_size == 0):
                        raise ValueError
                    pop_size = second_value
                except ValueError:   # Negative integer, 0, 1, string or float entered
                    if second_value == 1 and elite_size == 0:
                        print("Invalid number. Please enter an integer != 1")
                    else:
                        print("Invalid number. Please enter an integer >= " +\
                              str(elite_size) + " (number of elite routes).")
                continue

            elif value == 2:   # Change number of elite routes to pass down to next generation
                u_second_input = input("Please enter number of elite routes: ")
                try:
                    second_value = int(u_second_input)
                    # Demand positive integer or 0
                    # Also demand value less than number of routes per generation
                    if second_value < 0 or second_value >= pop_size:
                        raise ValueError
                    # Revert to value of 1 if integer = 0 and pop_size = 1
                    if second_value == 0 and pop_size == 1:
                        raise ValueError
                    elite_size = second_value
                except ValueError:   # Negative integer, string or float entered
                    if second_value == 0 and pop_size == 1:
                        print("Invalid number. Reverting to value of 1.")
                    else:
                        print("Invalid number. Please enter an integer >= 0 and < "\
                              + str(pop_size) +\
                              " (number of routes per generation).")
                continue

            elif value == 3:   # Change mutation rate
                u_second_input = input("Please enter mutation rate: ")
                try:
                    second_value = float(u_second_input)
                    # Probability, so demand float between 0 and 1
                    if second_value < 0 or second_value > 1:
                        raise ValueError
                    mutation_rate = second_value
                except ValueError:   # Integer, <0, >1 or string entered
                    print("Invalid number. Please enter a rational number between 0 and 1.")
                continue

            elif value == 4:   # Change random seed
                u_second_input = input("Please enter a random seed: ")
                try:
                    second_value = int(u_second_input)
                    if second_value < 0:   # Demand positive integer or 0
                        raise ValueError
                    # Assign random seed
                    random_seed = second_value
                except ValueError:   # Negative integer, string or float entered
                    print("Please enter an integer >= 0.")
                continue

            elif value == 5:   # Accept parameters and break while loop
                print("Parameters Accepted.")
                break

            else:
                print("Invalid choice. Please try again.")
                continue

        except ValueError:   # String or float entered
            if u_input == 'q':   # Exit program
                print("Exiting...\n")
                return None
            else:
                print("Invalid choice. Please try again.")
                continue

    # Return parameters for genetic algorithm
    return (n_generations, pop_size, elite_size, mutation_rate, random_seed)


def StartStationMenu(station_list):
    """StartStationMenu(station_list)
    Presents user with list of station names and asks user to select starting
    station.
    Returns starting Station object.
    Returns None if user wishes to exit program."""

    print("\n")
    print("--------------------------")
    print("Starting Station Selection")
    print("--------------------------")
    print("List of starting stations:")

    # Loop through Station objects in station list
    # Present user with station names and ask for input
    for idx, station in enumerate(station_list):
        print("[" + str(idx) + "]\t" + station.name)

    while True:
        u_input = input("Please select a starting station (q to quit): ")

        try:
            value = int(u_input)

            if value < 0:   # Demand positive integer only
                raise IndexError

            # Select starting station and display its name
            first_station = station_list[value]
            print("Starting station selected: " + str(first_station.name))
            # Ask user to confirm
            u_confirm = input("Is this correct? (q to quit): ")
            if u_confirm == 'q':   # Exit program
                first_station = None
                break
            # If starting station is correct, break while loop so that it can
            # be returned
            elif u_confirm == 'y' or u_confirm == 'Y':
                break
            # If starting station is incorrect, set starting station to None
            # and return to start of while loop
            elif u_confirm == 'n' or u_confirm == 'N':
                first_station = None
            # If invalid text entered for confirmation, ask user to enter
            # starting station again.
            else:
                print("Invalid choice.")
            continue

        except IndexError:   # Negative integer or out of range
            print("Invalid choice. Please try again.")
            continue
        except ValueError:   # String or float entered
            if u_input == 'q':   # Exit program
                print("Exiting...\n")
                first_station = None
                break
            else:
                print("Invalid choice. Please try again.")
                continue

    return first_station   # Return first Station object


def TimeAndDateMenu():
    """TimeAndDateMenu()
    Presents user with default time and date for journey planner search and
    asks whether these should be changed. Enforces strict formatting for user
    entered times and dates.
    Returns time and date in correct format for TfL Journey Planner API.
    Returns time = None and date = None if user wishes to exit program."""

    # Set default values
    time = "1200"
    date = DetermineDate()

    print("\n")
    print("-----------------")
    print("Set Time and Date")
    print("-----------------")

    while True:
        print("Please select an option: ")
        print("[0]\t Change time\t {}:{}".format(time[:2], time[2:]))
        print("[1]\t Change date\t {}-{}-{}".format(date[:4], date[4:6], date[6:]))
        print("[2]\t Accept these values")
        u_input = input("(q to quit): ")

        try:
            value = int(u_input)

            if value == 0:   # Prompt user to enter new time
                u_time_input = input("Please enter new time in 24-hour hh:mm format: ")
                # Check time entered in 24-hour hh:mm format
                if re.compile("\d{2}:\d{2}").match(u_time_input):
                    hh, mm = u_time_input.split(':')   # Grab hours and minutes
                    # Further check to ensure data integrity
                    if int(hh) < 24 and int(mm) <= 60:
                        time = u_time_input.replace(':', '')   # Remove :
                    else:
                        print("Invalid time. Please select another option.")
                else:
                    print("Invalid time. Please select another option.")
                continue

            elif value == 1:   # Prompt user to enter new date
                u_date_input = input("Please enter new date in YYYY-MM-DD format: ")
                date_today = datetime.datetime.now()
                date_next_year = date_today + datetime.timedelta(days=365)
                # Check date entered in YYYY-MM-DD format
                if re.compile("\d{4}-\d{2}-\d{2}").match(u_date_input):
                    YYYY, MM, DD = u_date_input.split('-')
                    try:
                        # Check for valid date by converting to datetime object
                        u_date = datetime.datetime(int(YYYY), int(MM), int(DD))
                        # Ensure date is not in past nor more than one year in
                        # the future
                        if u_date < date_today or u_date > date_next_year:
                            print("Please enter date between " +\
                                  date_today.strftime("%Y-%m-%d") + " and " +\
                                  date_next_year.strftime("%Y-%m-%d"))
                        else:
                            date = u_date_input.replace('-', '')   # Remove -

                    except TypeError:   # Invalid datetime object
                        print("Invalid date. Please select another option.")
                    except ValueError:   # Invalid date
                        print("Invalid date. Please select another option.")
                else:   # Date not entered as integers in YYYY-MM-DD format
                    print("Invalid date format. Please select another option.")
                continue

            elif value == 2:   # User accepts values
                break

            else:
                print("Invalid choice. Please try again.")
                continue

        except ValueError:
            if u_input == 'q':
                print("Exiting...\n")
                return None, None
            else:
                print("Invalid choice. Please try again.")
                continue

    return time, date   # Returns time and date


def CreateStationListMenu():
    """CreateStationListMenu()
    User menu to create list of Station objects. Mislabelled deliberately as
    "Create Station Matrix" as function eventually will lead to creation of
    station matrix, which details durations of journeys between stations.
    Returns list of Station objects if successful.
    Returns None if unsuccessful or user wishes to exit program."""

    print("\n")
    print("---------------------")
    print("Create Station Matrix")
    print("---------------------")

    try:
        # Try to find latest, existing station list file in station_lists
        # directory
        station_list_file = FMan.FindFile("station_lists", "txt")
        while True:
            print("Latest station list file: " + station_list_file)
            u_input = input("Would you like to use this file? (q to quit) ")

            if u_input == 'q':   # Exit program
                print("Exiting...\n")
                return None
            # Use latest station list file
            elif u_input == 'y' or u_input == 'Y':
                break
            # Select alternate station list file
            elif u_input == 'n' or u_input == 'N':
                list_of_files = FMan.FindFile("station_lists", "txt", 0)
                station_list_file = FMan.SelectFileFromList(list_of_files)
                break
            else:
                print("Please select a valid option (y/Y/n/N/q).\n")
                continue

    # If no station list file exists, FindFile() will return None
    # In this case, ask user to create a station list file
    except TypeError:
        print("No station list file found.", end=' ')
        print("Please create one in the ./station_lists/ directory.")
        return None

    # Create list of Station objects
    station_list = FMan.CreateStationList(station_list_file)

    return station_list   # Return list of Station objects


def RunGenAlg(station_matrix_file):
    """RunGenAlg(station_matrix_file)
    Calls user interface functions to set parameters for genetic algorithm.
    Then calls function to run genetic algorithm. Finally calls visualisation
    and statistics functions to plot the data and print out the best route.
    Returns True (good status) if all actions are successful.
    Returns False (bad status) if errors are encountered or user wishes to exit
    program.
    """

    # If station matrix file does not exist, create one
    if station_matrix_file == None:
        station_list = CreateStationListMenu()
        if station_list == None:   # In case of error return bad status
            return False
        time, date = TimeAndDateMenu()
        if time == None:   # If user wishes to quit, return bad status
            return False
        # Create station matrix
        status = FMan.CreateStationMatrix(station_list, time, date)
        if status == None:   # In case of error return bad status
            return False

    # If station matrix file exists, acquire data from it
    else:
        station_list = FMan.ReadStationMatrix(station_matrix_file)
        if station_list == None:   # In case of error return bad status
            return False
        time, date = FMan.StationMatrixTimeAndDate(station_matrix_file)

    # Ask user to select starting station from list of Station objects
    first_station = StartStationMenu(station_list)
    if first_station == None:   # If user wishes to quit, return bad status
        return False

    # Present user with default genetic algorithm parameters and ask for input
    gen_alg_pars = GeneticAlgorithmMenu()
    if gen_alg_pars == None:   # If user wishes to quit, return bad status
        return False

    # Run genetic algorithm and return data for performance anaylsis
    plot_pars = Galus.GeneticAlgorithm(station_list, first_station, *gen_alg_pars)
    # Plot returned data
    VSFun.FillCanvas(*plot_pars, time, date, gen_alg_pars[-1])

    # Output journey details for best route in final generation
    journey_details = VSFun.BuildJourney(plot_pars[2].iat[0,0], time, date, gen_alg_pars[-1])
    if journey_details == None:   # In case of error return bad status
        return False
    print("\n")
    print(journey_details)

    return True   # Return good status if no error


def MainMenu():
    """MainMenu()
    Main menu for user interface. Finds latest station matrix file and presents
    user with choice to proceed with this file, select an alternate or create a
    new one. The station matrix file is generated from a previous execution of
    this script and details durations of journeys between stations."""

    while True:
        print("---------------------------")
        print("Tube Challenge Route Finder")
        print("---------------------------")

        # Try to find latest, existing station matrix file in station_matrices
        # directory
        station_matrix_file = FMan.FindFile("station_matrices", "csv")

        try:
            print("Latest station matrix file: " + station_matrix_file)
        
        # If no station matrix files exist, FindFile() will return None
        # In this case, force creation of station matrix file
        except TypeError:
            print("No station matrix files found. Let's create a new one.")
            status = RunGenAlg(station_matrix_file=None)
            if status == False:   # End program in case of error
                break

        print("Please enter an option:")
        print("[0]\t Use this file")
        print("[1]\t Use alternate file")
        print("[2]\t Create new file")
        u_input = input("(q to quit): ")

        try:
            value = int(u_input)


        except ValueError:   # If string or float entered
            if u_input == 'q':   # Exit program
                print("Exiting...\n")
                break
            # Present options to user again if "q" not entered
            else:
                print("Invalid choice. Please try again.\n")
                continue

        if value == 0:   # Use latest station matrix file
            status = RunGenAlg(station_matrix_file)
        # If user wishes to use another station matrix file, present
        # list of csv files from which to choose
        elif value == 1:
            list_of_files = FMan.FindFile("station_matrices", "csv", 0)
            station_matrix_file = FMan.SelectFileFromList(list_of_files)
            status = RunGenAlg(station_matrix_file)
        elif value == 2:   # Create new station matrix file
            status = RunGenAlg(station_matrix_file=None)
        # Present options to user again if integer entered is not 0, 1
        # or 2
        else:
            print("Invalid choice. Please try again.\n")
            continue

        if status == False:   # End program in case of error
            break
        else:
            continue


# Execute user interface
MainMenu()
