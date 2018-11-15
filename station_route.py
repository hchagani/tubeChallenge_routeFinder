# Definition of Station and Route classes for genetic algorithm to find
# quickest routes between London Underground stations.
# v1.0
# Hassan Chagani 2018-11-09
"""
Definition of Station and Route classes for genetic algorithm to find quickest
routes between London Underground stations.
"""

class Station:
    """Station(name, id_no)
    Station class declaration."""

    def __init__(self, name, id_no):
        self.name = str(name)
        self.id_no = str(id_no)
        self.time_to = {}   # Time to other stations

    def SetTimeTo(self, station_list, duration_list):
        """SetTimeTo(station_list, duration_list)
        Set time to other Station objects."""
        self.time_to = dict(zip(station_list, duration_list))

    def __repr__(self):
        return self.name   # Output station name


class Route:
    """Route(path)
    Route class declaration, where path is list of Station objects."""

    def __init__(self, path):
        self.path = path
        # Iterate over Stations in path to find total duration of journey
        duration = 0
        for i in range(len(self.path) - 1):
            from_station = self.path[i]
            to_station = self.path[i+1]
            duration += from_station.time_to[to_station]
        self.time_taken = duration

    def __repr__(self):
        return str(self.path)   # Output route as list of Station objects
