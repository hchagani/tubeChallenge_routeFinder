# Visualisation and statistics functions for genetic algorithm to find quickest
# routes between London Underground stations.
# v1.0
# Hassan Chagani 2018-11-14
"""
Visualisation and statistics functions for genetic algorithm to find quickest
routes between London Underground stations
"""

import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# Import miscellaneous functions
import misc_fun as MFun


def FindChiSquare(final_gen_CDF):
    """FindChiSquare(final_gen_CDF)
    Find \chi^2/NDF, where \chi^2 = \sum_i{(O_i - E_i)^2 / E_i}, where O and E
    are observed and expected values respectively from generation i = 0...n.
    This value is used to compare the Cummulative Distribution Function (CDF)
    of Route object fitnesses from the last generation with that expected from
    a homogeneous population (i.e. a straight line). The closer the value is to
    0, the more homogeneous the population.
    Returns \chi^2/NDF."""

    # Find contribution to \chi^2 from each route
    # Expected value = x / number of routes as y = x / number of routes + 0 for
    # homogeneous population, where x = route
    chi_sq = (final_gen_CDF - final_gen_CDF.index / float(len(final_gen_CDF)-1)) ** 2\
              / (final_gen_CDF.index/ float(len(final_gen_CDF)))

    # Division by zero error for psuedo-route 0, so fill with 0
    chi_sq = chi_sq.fillna(0)
    
    # Return \chi^2/NDF
    # NDF = number of routes - 2 variables from linear fit - 1
    # Number of routes = len(final_gen_CDF) - 1
    return chi_sq.sum() / (len(final_gen_CDF) - 4)


def DecayEq(x, T0, tau, plateau):
    """DecayEq(x, T0, tau, plateau)
    Models exponential decay of journey times of best routes with generation.
    As journey times of routes will be non-zero, a plateau term is added.
    Returns journey time as a function of initial journey time T0, the decay
    constant tau and the time to which the journey time plateaus."""

    return (T0 - plateau) * np.exp(-x / tau) + plateau


def FillCanvas(best_route_gen, mean_sigma_gen, final_gen_df, time, date,\
               random_seed):
    """FillCanvas(best_route_gen, mean_sigma_gen, final_gen_df, time, date,\
                  random_seed)
    Plots the following relationships to equip user with tools to determine
    which changes to make when re-running the genetic algorithm:
        1. Duration of best route per generation.
            - Should be modelled by exponential decay.
            - Exponential decay function fitted to data to give user an idea of
              plateau time and decay constant.
        2. Distribution of route durations in final generation.
            - Gives user the range of route durations in final generation and
              distribution of these durations.
        3. Mean duration and standard deviation from mean per generation.
            - Standard deviation represented by green shaded area around black
              line that represents the mean.
            - Gives user an idea of the spread of route durations with
              generation.
        4. Cumulative Distribution Function (CDF) of final generation route
           fitnesses.
            - Should be a straight line if all routes are of identical
              duration.
            - Calculated \chi^2/NDF gives user an idea of the homogeneity of
              route durations."""

    # Numpy array of generation indices
    generations = np.arange(len(best_route_gen))

    fig = plt.figure(figsize=(15, 8))

    # Top left
    # Duration of best route per generation
    plt.subplot(2,2,1)
    plt.grid()
    plt.plot(generations, best_route_gen, color='k')
    plt.title("Duration of Best Route per Generation")
    plt.xlabel("Generation / G")
    plt.ylabel("Duration (minutes) / T")
    # Fit decay equation to distribution
    # Zeroth generation provides estimate for initial duration
    # Decay constant estimate given by half-life estimate / ln(2)
    # Final generation duration provides estimate for plateau
    initial_T0 = best_route_gen[0]
    half_life_ypos = best_route_gen[0] - ((best_route_gen[0] - best_route_gen[-1]) / 2.)
    for gen in generations:
        if best_route_gen[gen] < half_life_ypos:
            half_life_est = gen
            break
        else:   # If there is no improvement and hence no decay
            half_life_est = 0
    initial_tau = half_life_est / np.log(2)
    initial_plateau = best_route_gen[-1]
    # Only fit decay equation if there is a decay
    if half_life_est != 0:
        popt, pcov = curve_fit(DecayEq, generations, best_route_gen,\
                               p0=[initial_T0, initial_tau, initial_plateau])
        decay_eq_str =\
            r"$T = {:.0f}e^{{\left(-G/{:.0f}\right)}} + {:.02f}$".format(popt[0]-popt[2],\
                                                                         popt[1], popt[2])
        decay_eq_fit = np.linspace(generations[0], generations[-1],\
                                   len(generations)*5)
        plt.plot(decay_eq_fit, DecayEq(decay_eq_fit, *popt), color='r',\
                 linestyle='dashed', label=decay_eq_str)
        plt.legend(loc="upper right")

    # Top right
    # Distribution of route durations in final generation
    plt.subplot(2,2,2)
    plt.grid()
    # Find range of data and set bin width at 1 minute
    duration_range = int(final_gen_df.Duration.iat[-1] - final_gen_df.Duration.iat[0]) + 1
    plt.hist(final_gen_df.Duration, bins=duration_range, color='g')
    plt.title("Final Generation: Distribution of Route Durations")
    plt.xlabel("Durations (minutes)")
    plt.ylabel("Number of Routes")

    # Bottom left
    # Mean duration and standard deviation from mean per generation
    # Mean is represented by line
    # Standard deviation represented by filled area
    plt.subplot(2,2,3)
    plt.grid()
    plt.plot(generations, mean_sigma_gen[:,0], color='k')
    plt.fill_between(generations, mean_sigma_gen[:,0]-mean_sigma_gen[:,1],\
                     mean_sigma_gen[:,0]+mean_sigma_gen[:,1], alpha=0.2,
                     edgecolor='g', facecolor='g')
    plt.title("Mean Duration and Standard Deviation from Mean")
    plt.xlabel("Generation")
    plt.ylabel("Duration (minutes)")

    # Bottom right
    # Cummulative Distribution Function (CDF) of final generation route fitnesses
    plt.subplot(2,2,4)
    plt.grid()
    last_entry = pd.Series([1.0])
    final_gen_CDF = pd.concat([final_gen_df.CDF, last_entry], ignore_index=True)
    final_gen_CDF = final_gen_CDF.shift()
    final_gen_CDF[0] = 0.0
    plt.plot(final_gen_CDF.index, final_gen_CDF, color='k',\
             label="CDF of final generation")
    # Also plot CDF if all routes were the same
    plt.plot([final_gen_CDF.index[0], final_gen_CDF.index[-1]], [0.0, 1.0],\
             color='r', linestyle='dashed',\
             label="CDF of homogeneous population")
    plt.legend(loc='upper left')
    plt.title("Final Generation: CDF of Route Fitnesses")
    plt.xlabel("Route")
    plt.ylabel("Cumulative Sum / Sum")
    # Show \chi^2/NDF value on plot. The closer this value is to 0, the more
    # homogeneous the routes that comprise the final generation.
    plt.annotate(r"$\frac{{\chi^2}}{{NDF}}$ = {:.3e}".format(FindChiSquare(final_gen_CDF)),\
                 xy=(0.75, 0.1), xycoords='axes fraction',\
                 bbox={'boxstyle':'square', 'fc':'w', 'ec':'k'})

    fig.tight_layout()
    plt.show()

    fig.savefig("./output_routes/" + date + "_" + time + "_" + str(random_seed)\
                + ".png", format='png')


def BuildJourney(best_route, time, date, random_seed):
    """BuildJourney(best_route, time, date, random_seed)
    Feeds best route from final generation into Transport for London (TfL) API.
    Returns string with route detailing departure and arrival times, and
    instructions.
    Returns None if error encountered with TfL API.
    """

    # Preserve intial time for output file name
    initial_time = time
    # Begin journey string with first Station object in Route object
    journey = best_route.path[0].name.upper() + "\n"

    print("\nFinding route:")

    # Loop over Station objects that form best route to find journey times
    for start_station, end_station in zip(best_route.path[:-1], best_route.path[1:]):

        tfl_jp_url = MFun.BuildJPlannerURL(start_station.id_no,\
                                           end_station.id_no, time, date)

        print("From " + start_station.name)
        print("\tto " + end_station.name, end="...")

        # Get journey data from TfL API
        journey_data = MFun.ContactTfLAPI(tfl_jp_url)
        if journey_data == None:
            return None

        # Number of journeys returned by TfL API
        n_journeys = len(journey_data['journeys'])

        # Convert date and time to datetime object to allow comparison
        time_dt = datetime.datetime(int(date[:4]), int(date[4:6]), int(date[6:]),\
                                    int(time[:2]), int(time[2:]))

        # Ensure departure time occurs after requested time
        for j in range(n_journeys):

            # Get departure time of first leg of journey
            d_time = journey_data['journeys'][j]['legs'][0]['departureTime']
            # Convert departure time to datetime object
            d_time_dt = MFun.DateTimeConversion(d_time)
            # Only use this journey if departure time occurs after or at
            # requested time
            if d_time_dt >= time_dt:
                journey_idx = j
                break

        # Number of legs in journey
        n_legs = len(journey_data['journeys'][journey_idx]['legs'])

        # Loop over each leg of journey and add to journey string
        for leg in range(n_legs):
            # Find departure time of leg
            leg_d_time = journey_data['journeys'][journey_idx]['legs'][leg]['departureTime']
            # Convert departure time to datetime object
            leg_d_time_dt = MFun.DateTimeConversion(leg_d_time)
            # Store departure time of first leg of first journey
            if start_station == best_route.path[0] and leg == 0:
                first_d_time = leg_d_time_dt
            leg_d_time = "{:02d}:{:02d}".format(leg_d_time_dt.hour,\
                                                leg_d_time_dt.minute)
            journey += leg_d_time + " - "   # Append to journey string

            # Find arrival time of leg
            leg_a_time = journey_data['journeys'][journey_idx]['legs'][leg]['arrivalTime']
            # Convert arrival time to datetime object
            leg_a_time_dt = MFun.DateTimeConversion(leg_a_time)
            # Store arrival time of last leg of final journey as datetime object
            if end_station == best_route.path[-1] and leg == n_legs-1:
                final_a_time = leg_a_time_dt
            leg_a_time = "{:02d}:{:02d}".format(leg_a_time_dt.hour,\
                                                leg_a_time_dt.minute)
            journey += leg_a_time + "\t"   # Append to journey string
            # Extract date and time for next journey query if last leg
            if leg == n_legs-1:
                date = "{:04d}{:02d}{:02d}".format(leg_a_time_dt.year,\
                                                   leg_a_time_dt.month,\
                                                   leg_a_time_dt.day)
                time = leg_a_time.replace(':', '')

            # Get leg instructions
            leg_instruct = journey_data['journeys'][journey_idx]['legs'][leg]['instruction']['summary']

            # Upper case for final station on last leg
            if leg == n_legs-1:
                # If final leg is by underground train
                if " to " in leg_instruct:
                    final_station = leg_instruct[leg_instruct.index(" to ")+4:]
                    leg_instruct = leg_instruct.replace(final_station, final_station.upper())
                # If final leg is on foot
                elif " at " in leg_instruct:
                    final_station = leg_instruct[leg_instruct.index(" at ")+4:]
                    leg_instruct = leg_instruct.replace(final_station, final_station.upper())
                # Otherwise do nothing
            journey += leg_instruct + "\n"

    # Output journey time from station matrix in hh:mm format
    journey = "Journey duration from station matrix: " +\
              "{:02.0f}:{:02.0f}".format(best_route.time_taken//60,\
                                         best_route.time_taken%60) + "\n" + journey

    # Find journey time from TfL journey planner in minutes
    tfl_jp_delta_time = (final_a_time - first_d_time).total_seconds() // 60
    # Output journey time from TfL journey planner in hh:mm format
    journey = "Journey duration from TfL Journey Planner: " +\
              "{:02.0f}:{:02.0f}".format(tfl_jp_delta_time//60,\
                                         tfl_jp_delta_time%60) + "\n" + journey

    # Write details of final journey to file
    # File name given by YYYYMMDD_hhmm_<random_seed>.dat
    journey_filename = "./output_routes/" + date + "_" + initial_time + "_" +\
                       str(random_seed) + ".dat"
    with open(journey_filename, 'w') as journey_file:
        journey_file.write(journey)

    return journey   # Return string containing journey details
