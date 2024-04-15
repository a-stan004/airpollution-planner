import osmnx as ox
import networkx as nx
import geopandas as gpd
# import matplotlib.pyplot as plt
import pandas as pd
from geopy import Nominatim

# ==========================================================================
# Gathering inputs and geocoding
# ==========================================================================


class Inputs:
    """
    Class representing user inputs

    Attributes
    ----------
    initial : str
        initial location
    target : str
        target location

    Methods
    -------
    None
    """
    def __init__(self, initial, target):
        """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
        initial : str
            inital location
        target : str
            target location
        """

        self.initial = initial
        self.target = target


# Creates class instance of Inputs with two user inputs
userinputs = Inputs("WS79LQ", "WS79JP")


# Address locator function is set up to geocode locations using geopy nominatim
def geocodeaddresses(location):
    """Adds locational context to user input

        Parameters:
        location (string): User input of location as string

        Returns:
        tuple: Address, latitude and longtitude

    """
    # Class instance created for nominatim tool
    loc = Nominatim(user_agent="Geopy Library")
    geocoded = loc.geocode(location)
    address = geocoded.address
    latitude = geocoded.latitude
    longtitude = geocoded.longitude
    return address, latitude, longtitude


geo_initial = geocodeaddresses(userinputs.initial)
geo_target = geocodeaddresses(userinputs.target)


# ==========================================================================
# Constructing a graph for the area
# ==========================================================================

class Route:

    def __init__(self, places, latitudes, longitudes):
        self.places = places
        self.latitudes = latitudes
        self.longitudes = longitudes

    def gpdframe(self):
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
        orig_node = ox.nearest_nodes(graph, self.longitudes[0], self.latitudes[0])
        target_node = ox.nearest_nodes(graph, self.longitudes[1], self.latitudes[1])
        return orig_node, target_node


userroute = Route(
    [geo_initial[0], geo_target[0]],
    [geo_initial[1], geo_target[1]],
    [geo_initial[2], geo_target[2]]
)

gdf = userroute.gpdframe()

# Creating a polygon of the search area
box = gdf.unary_union.envelope

# Expanding the search area using a buffer so that routes are not limited
buffbox = box.buffer(0.01)

# Drawing the graph using OSMnx
graph = ox.graph_from_polygon(buffbox, network_type='walk', truncate_by_edge=False, retain_all=True)
# fig, ax = ox.plot_graph(graph)

# ==========================================================================
# Drawing an initial route between locations
# ==========================================================================

nodes = userroute.getnodes()

route = nx.shortest_path(G=graph, source=nodes[0], target=nodes[1], weight='distance')
fig, ax = ox.plot_graph_route(graph, route)

# ==========================================================================
# Gathering locations of nodes along route and checking pollution values
# ==========================================================================

nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
route_nodes = nodes.loc[route]
