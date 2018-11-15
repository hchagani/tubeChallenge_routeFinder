# Genetic algorithm to find quickest routes between London Underground
# stations.
# v1.0
# Hassan Chagani 2018-11-13
"""
Genetic algorithm to find quickest routes between London Underground stations.
"""

import numpy as np
import pandas as pd
import random

# Import Station and Route classes
from station_route import Station, Route


def CreateRoute(station_list, first_station):
    """CreateRoute(station_list, first_station)
    Create Route object given starting Station object and list of Station
    objects. Places starting Station object at beginning of journey and
    randomises remaining Station objects along path to create random Route
    object.
    Returns Route object."""

    # Copy list of Station objects to new list so contents can be altered
    # without affecting original list of Station objects.
    path = station_list[:]
    # Remove starting Station object from list, randomise entries and then
    # insert starting Station object at the beginning. This becomes the order
    # in which stations are visited (i.e. the path).
    path.remove(first_station)
    path = random.sample(path, len(path))
    path.insert(0, first_station)

    route = Route(path)   # Create Route object from path

    return route   # Return Route object


def CreateInitialPopulation(pop_size, station_list, first_station):
    """CreateInitialPopulation(pop_size, station_list, first_station)
    Create first generation (labelled 0th generation) list of Route objects.
    Returns list of Route objects."""

    population = []   # Initialise empty route list

    # Generate routes to fill initial population size
    for route in range(pop_size):
        population.append(CreateRoute(station_list, first_station))

    return population   # Return list of routes


def SortRoutes(population):
    """SortRoutes(population)
    Sorts Route objects by duration.
    Returns sorted list of Route objects."""

    # Sort Route objects by duration and return sorted list of Route objects
    return sorted(population, key=lambda route: route.time_taken)


def SetParentsFitness(sorted_routes):
    """SetParentsFitness(sorted_routes)
    Create pandas dataframe from sorted list of Route objects. Define fitness
    of Route objects as reciprocal of its duration, making quicker Route
    objects fitter than slower ones. Calculate Cumulative Distribution Function
    (CDF) using fitness values to enable fitness proportion selection.
    Returns pandas dataframe."""

    # Create pandas dataframe with single column of Route objects
    parents = pd.DataFrame(sorted_routes, columns=["Route"])

    # Define Fitness of Route objects as reciprocal of journey duration and
    # create column for Fitness
    parents["Fitness"] = 1. / parents.Route.apply(lambda route: route.time_taken)

    # Calculate cumulative sum of Fitnesses and divide this by sum of Fitnesses
    # to obtain Cumulative Distribution Function (CDF). Route objects already
    # sorted so no need to re-sort by Fitness to enable CDF generation.
    parents["Cum_Sum"] = parents.Fitness.cumsum()
    parents["CDF"] = parents.Cum_Sum / parents.Fitness.sum()

    return parents   # Return parents fitness pandas dataframe


def SelectParents(parents, elite_size):
    """SelectParents(parents, elite_size)
    Select pairs of Route objects to act as mothers and fathers to create next
    generation. Number of parent-pairs are given by number of elite routes to
    pass on to next generation subtracted from number of routes per generation.
    Uses fitness proportionate selection to get Route objects.
    Returns two lists of Route objects to represent each parent.
    """

    # Initialise empty lists for mother and father Route objects
    # mother[i] will mate with father[i], where i = 0...(n-1),
    # where n = (number of routes per generation) - (number of elite routes)
    mother = []
    father = []

    # Create each mother-father pair one-by-one
    for mating in range(parents.shape[0] - elite_size):

        pick_mother = random.random()
        pick_father = random.random()
        mother_selected = False
        father_selected = False

        # Loop over dataframe of parents comparing random numbers generated for
        # mother and father selections above with Cumulative Distribution
        # Function (CDF) for fitness proportionate selection
        for parent in range(parents.shape[0]):

            # Once random number for mother selection <= CDF for Route object
            # in dataframe, mother = Route object
            if pick_mother <= parents.iat[parent, 3] and mother_selected == False:

                mother.append(parents.iat[parent, 0])
                mother_selected = True

            # Once random number for father selection <= CDF for Route object
            # in dataframe, father = Route object
            if pick_father <= parents.iat[parent, 3] and father_selected == False:

                father.append(parents.iat[parent, 0])
                father_selected = True

            # Once mother and father have been selected, ensure mother and
            # father are not the same
            if mother_selected == True and father_selected == True:

                # If mother and father are the same, reroll random number for
                # father selection until this is not longer the case
                while mother[-1] == father[-1]:

                    pick_father = random.random()

                    for m_parent in range(parents.shape[0]):

                        if pick_father <= parents.iat[m_parent, 3]:

                            father[-1] = parents.iat[m_parent, 0]
                            # Once new father is selected, stop selection to
                            # check whether mother and father are the same
                            break

                break   # Once mother and father are selected, stop selection

    # Return mother and father pairs as lists
    return mother, father


def Procreate(parents, elite_size):
    """Procreate(parents, elite_size)
    Create next generation of Route objects. User defined number of elite
    routes automatically pass on to next generation. The remaning routes are
    derived by splicing Station objects from mother and father pairs to create
    children. Two random integers from 1 (to preserve the first station) to
    (n-1), where n is the number of Station objects that form the Route object,
    give first and last indices. This is to ensure that at least the first and
    last Station objects from the mother are passed on to the child so that the
    child differs from the father. Station objects that lie within these bounds
    are not passed on to the child from the mother. They are passed on to the
    child from the father according to their order and position in the father's
    list of Station objects.
    Returns list of Route objects to form next generation.
    
    An illustrative example of this process is given below:    
        mother = [A, B, C, D, E, F]
        father = [A, F, B, E, D, C]
    
    Assuming random integers generated are 2 and 5,
    Station objects passed on from mother and father:
        mother's contribution = [A, C, F]
        father's contribution = [B, E, D]
    
    Now splice Station objects from father to complete child:
        child = [A, C, B, E, D, F]"""


    # Initialise empty list for next generation Route objects
    children = []

    # User defined number of quickest Route objects automatically carry over to
    # next generation
    for elite in range(elite_size):
        children.append(parents.iat[elite, 0])

    # Get list of mothers and fathers to procreate next generation
    mother, father = SelectParents(parents, elite_size)

    # Commence procreation
    for mating in range(len(mother)):

        # Keep first station the same as mother's, so generate two random
        # integers from index 1 to index n-1, where n is length of list of
        # Route objects. This ensures that at least the first and last Station
        # objects are inherited from the mother to avoid reproducing the
        # father.
        genes = [random.randint(1, len(father[mating].path)-1),\
                 random.randint(1, len(father[mating].path)-1)]

        # If both random integers are the same, reroll second one until they
        # aren't
        while genes[0] == genes[1]:
            genes[1] = random.randint(1, len(father[mating].path)-1)

        # Find first and last genes to splice
        first_gene = min(genes)
        last_gene = max(genes)

        # Copy mother's path to that of her child temporarily
        child = mother[mating].path[:]

        # Remove Station objects that will be passed on from father
        for gene in father[mating].path[first_gene:last_gene]:
            child.remove(gene)

        # Insert Station objects from father in child's list to match their
        # positions in father's list
        for gene in father[mating].path[first_gene:last_gene]:
            child.insert(father[mating].path.index(gene), gene)

        # Add child Route object to next generation
        children.append(Route(child))

    return children   # Return list of Route objects to form next generation


def Mutate(children, mutation_rate):
    """Mutate(children, mutation_rate)
    Determines whether Route objects should undergo mutation according to
    user-specified mutation rate. Mutation process involves swapping positions,
    determined from the generation of two random integers, of two Station
    objects in the list that forms Route object selected for mutation. This is
    done to avoid reaching a false minimum through iteration, by introducing
    variation in the population, thus strengthening it."""

    # For each Route object in this generation, determine whether mutation
    # should occur through comparison of random number generated with
    # user-specified mutation rate
    for child in range(len(children)):

        mutate_roll = random.random()

        # Only if mutation rate exceeds or is equal to random number generated,
        # swap Station objects in list that forms Route
        if mutate_roll <= mutation_rate:

            # Copy Route object to temporary variable and delete it from list
            # Route objects
            mutate_path = children[child].path[:]
            del children[child]

            # Generate two random integers to determine which Station objects
            # to swap
            genes = [random.randint(1, len(mutate_path)-1),\
                     random.randint(1, len(mutate_path)-1)]

            # If both Station objects are the same, reroll second one until
            # they aren't
            while genes[0] == genes[1]:
                genes[1] = random.randint(1, len(mutate_path)-1)

            # Swap Station objects
            mutate_path[genes[0]], mutate_path[genes[1]]\
                    = mutate_path[genes[1]], mutate_path[genes[0]]

            # Reinsert mutated Route object in list
            children.insert(child, Route(mutate_path))

    return children   # Return list of Route objects to form next generation


def CreateNextGeneration(previous_generation, elite_size, mutation_rate):
    """CreateNextGeneration(previous_generation, elite_size, mutation_rate)
    Calls functions to create next generation of Route objects.
    Returns next generation as list of Route objects."""

    # Get pandas dataframe of sorted Route objects with column to enable
    # fitness proportion selection
    parents = SetParentsFitness(previous_generation)

    # Create next generation
    children = Procreate(parents, elite_size)

    # Switch Station objects within list that forms Route objects according to
    # user-defined rate. This is done in an effort to avoid reaching false
    # minima and thus never reaching close to the most optimal route.
    next_generation = Mutate(children, mutation_rate)

    # Sort Route objects by duration
    sorted_next_generation = SortRoutes(next_generation)

    # Return next generation of sorted Route objects
    return sorted_next_generation


def GeneticAlgorithm(station_list, first_station, n_generations, pop_size,\
                     elite_size, mutation_rate, random_seed):
    """GeneticAlgorithm(station_list, first_station, n_generations, pop_size,\
                        elite_size, mutation_rate, random_seed)
    Calls functions to perform genetic algorithm.
    Returns tuple of:
        journey durations of best routes from each generation as list;
        mean and standard deviations of routes from each generation as 2-D
            numpy array;
        pandas dataframe of routes that form final generation."""

    # Set random seed
    random.seed(random_seed)

    # Create initial population of routes
    population = CreateInitialPopulation(pop_size, station_list, first_station)
    # Sort Route objects in initial population by duration
    population = SortRoutes(population)

    # Duration of best route per generation
    # First entry is for initial population (Generation 0)
    best_route_gen = [population[0].time_taken]
    # Mean duration and standard deviation from mean per generation
    # First entry is for initial population (Generation 0)
    route_durations = np.array([route.time_taken for route in population])
    mean_sigma_gen = ([[np.mean(route_durations), np.std(route_durations)]])

    # Create next generations
    for gen in range(n_generations):

        population = CreateNextGeneration(population, elite_size, mutation_rate)

        # Generation 0 is initial generation, so start from 1
        print("Generation = " + str(gen+1))

        # Keep duration of best route per generation
        best_route_gen.append(population[0].time_taken)
        # Keep mean duration and standard deviation from mean per generation
        route_durations = np.array([route.time_taken for route in population])
        mean_sigma_gen.append([np.mean(route_durations),\
                               np.std(route_durations)])

    # Reuse SetParentsFitness() function to create pandas dataframe of Route
    # objects that form final generation. Then add a column for route duration.
    final_gen_df = SetParentsFitness(population)
    final_gen_df["Duration"] = final_gen_df.Route.apply(lambda route: route.time_taken)

    return (best_route_gen, np.array(mean_sigma_gen), final_gen_df)
