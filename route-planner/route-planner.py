import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
from geopy import Nominatim
from networkx import NetworkXNoPath
from raster import obtainvalue

# Safe limits for air pollution 2021 and 2005 WHO
WHO2025 = {
    "pm2_5": 1,
    "pm10": 5,
    "no2": 3
}
WHO2021 = {
    "pm2_5": 5,
    "pm10": 15,
    "no2": 10
}
WHO2005 = {
    "pm2_5": 10,
    "pm10": 20,
    "no2": 40
}

# ==========================================================================
# Gathering inputs and geocoding
# ==========================================================================


class Inputs:
    """
    Class representing user inputs

    Attributes
        initial (str): Inital location
        target (str): Target location

    Methods
        .__init___(): Constructs the object
        .geocodeaddresses(): Geocodes the inputs

    """
    def __init__(self, initial, target):
        """
        Constructs all the necessary attributes for the person object.

        Args
            initial(str): Initial location
            target(str): Target location

        Returns
            None
        """

        self.initial = initial
        self.target = target

    def geocodeaddresses(self):
        """
        Adds locational context to user input

        Args

        Returns
            geocodeinit (list): Initial address, latitude and longtitude
            geocodetarget (list): Target address, latitude and longtitude

        """
        # Class instance created for nominatim tool
        loc = Nominatim(user_agent="Geopy Library")
        initloc = loc.geocode(self.initial)
        geocodeinit = [initloc.address, initloc.latitude, initloc.longitude]
        targetloc = loc.geocode(self.target)
        geocodetarget = [targetloc.address, targetloc.latitude, targetloc.longitude]
        return geocodeinit, geocodetarget


# Creates class instance of Inputs with two user inputs
userinputs = Inputs("Wembley Stadium", "Tower Bridge")

geo_initial = userinputs.geocodeaddresses()[0]
geo_target = userinputs.geocodeaddresses()[1]

# ==========================================================================
# Constructing a graph for the area
# ==========================================================================


class Locations:
    """
    Class representing users locations

    Attributes
        places (list): List of addresses
        latitudes (list): List of latitudes
        longtitudes (list): List of longtitudes

    Methods
        .__init___(): Constructs the object
        .gpdframe(): Constructs a geopandas frame from the inputs with CRS 4326 geometry
        .getnodes(): Returns the closest nodes to the inital and target locations

    """

    def __init__(self, places, latitudes, longitudes):
        """
        Constructs all the necessary attributes for the locations object.

        Args
            places (list): List of addresses
            latitudes (list): List of latitudes
            longtitudes (list): List of longtitudes

        Returns
            None
        """
        self.places = places
        self.latitudes = latitudes
        self.longitudes = longitudes

    def gpdframe(self):
        """
        Constructs a geopandas frame from the inputs with CRS 4326 geometry

        Args

        Returns
            geodf(geopandas.geodataframe.GeoDataFrame): Geodataframe of the given inputs
        """
        df = pd.DataFrame({
            "Places": self.places,
            "Latitudes": self.latitudes,
            "Longitudes": self.longitudes,
        })
        geodf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.Longitudes, df.Latitudes), crs="EPSG:4326"
        )
        return geodf

    def getnodes(self):
        """
        Returns the closest nodes to the inital and target locations

        Args

        Returns
            orig_node (int): Node ID of nearest node on graph to initial location
            target_node (int): Node ID of nearest node on graph to target location
        """
        orig_node = ox.nearest_nodes(graph, self.longitudes[0], self.latitudes[0])
        target_node = ox.nearest_nodes(graph, self.longitudes[1], self.latitudes[1])
        return orig_node, target_node


# Creates an instance of the Locations class from the users earlier inputs
userlocations = Locations(
    [geo_initial[0], geo_target[0]],
    [geo_initial[1], geo_target[1]],
    [geo_initial[2], geo_target[2]],
)

# Variable created to store the geopandas data frame
gdf = userlocations.gpdframe()

# Creating a polygon of the search area
box = gdf.unary_union.envelope

# Expanding the search area using a buffer so that routes are not limited
buffbox = box.buffer(0.01)

# Constructing the graph using OSMnx
graph = ox.graph_from_polygon(buffbox, network_type='bike', truncate_by_edge=False, retain_all=True)

# Getting inital user locations and drawing initial graph and route
usernodes = userlocations.getnodes()
route = nx.shortest_path(G=graph, source=usernodes[0], target=usernodes[1], weight="distance")
fig, ax = ox.plot_graph_route(graph, route)

# Get initial limiter values
print("Start path finding ...")
pm2_5value = float(WHO2005["pm2_5"])
pm10value = float(WHO2005["pm10"])
no2value = float(WHO2005["no2"])

# Collect into tuple and define inital tolerance
limits = (pm2_5value, pm10value, no2value)
tolerance = 1

# Set up a location to store pollution values that are high
geo_cache = {}

# Take graph and make it into a geodataframe
geo_data = ox.graph_to_gdfs(graph, nodes=True, edges=False)


def get_location(node):
    """
    Takes a node as input and returns its x and y values

    Args
        node (dict): OSMnx type node
    Returns
        x (int): Value from x field of node dataframe
        y (int): Value from y field of node dataframe
    """
    row = geo_data.loc[node]
    x = row.x
    y = row.y
    return x, y


def get_geo_data(node):
    """
    Takes a node as input and gathers pollution data about node, uses obtainvalue function from raster script
    Requires geocache dictionary to be setup prior i.e. geo_cache={}

    Args
        node (dict): OSMnx type node
    Returns
        node (dict): Node added directly to geocache
    """
    if node not in geo_cache.keys():
        x, y = get_location(node)
        geo_cache[node] = (
            obtainvalue(y, x, "pm2.5"),
            obtainvalue(y, x, "pm10"),
            obtainvalue(y, x, "no2"),
        )
    return geo_cache[node]


def compare(values, limiters):
    """
    Compares node pollution values to limits

    Args
        values (dict): OSMnx node dictionary
    Returns
        within (bool): Returns true if all values are within limits
    """
    within = all(value < limiter * tolerance for value, limiter in zip(values, limiters))
    return within


# Unordered sets created to store nodes
all_nodes = set(graph.nodes())
bad_nodes = set()


def good_node(node):
    """
    Checks whether a node is a start or finish node (automatically skipped), and if it is within allowed limits

    Args
        node (dict): OSMnx node dictionary
    Returns
        goodbool (bool): Returns true if value is within limits or start/end node
    """
    if node in usernodes:
        return True
    goodbool = compare(get_geo_data(node), limits)
    return goodbool


def process_path(path):
    """
    Checks all the nodes in a route for nodes exceeding limits, and adds these to a list of bad nodes
    Requires creation of an empty set for bad nodes i.e. bad_nodes = set()

    Args
        path (list): List of node dictionaries as OSMnx route
    Returns
        good_path (bool): Returns true if all values are within limits
    """
    good_path = True
    for node in path:
        if not good_node(node):
            bad_nodes.add(node)
            good_path = False
    return good_path


def restricted_path(res_graph):
    """
    Tries to constuct a path with the high pollution value nodes removed.
    Where this is not possible a False statement is returned

    Args
        res_graph (MultiDiGraph): OSMnx pre-built graph as input
    Returns
        short_path (list): List of node dictionaries as OSMnx route if successful or False
    """
    nodes = all_nodes - bad_nodes
    sub = nx.subgraph(res_graph, nodes)
    try:
        short_path = nx.shortest_path(sub, source=usernodes[0], target=usernodes[1], weight="distance")
        return short_path
    except NetworkXNoPath:
        return False


# Attempts to make a valid path
valid_path = process_path(route)
# route_possible = True

# Counter for how many attempts
counter = 1
attempt = []

# Where valid path has not been found, while loop reattempts route by resetting bad nodes and upping limit tolerances
while not valid_path:
    print(f"Attempt: {counter}, tolerance:{tolerance}")
    attempt = restricted_path(graph)
    counter += 1
    if not attempt:
        tolerance *= 1.5
        bad_nodes = set()
    else:
        valid_path = process_path(attempt)

print("Path found")
fig, ax = ox.plot_graph_route(graph, attempt)

