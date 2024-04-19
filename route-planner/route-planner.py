import osmnx as ox
import networkx as nx
import geopandas as gpd
# import matplotlib.pyplot as plt
import pandas as pd
from geopy import Nominatim
from airpollutionAPI import PointQuality
from raster import obtainvalue

# Safe limits for air pollution 2021 and 2005 WHO
WHO2021 = {
    "pm2.5": 5,
    "pm10": 15,
    "no2": 10
}
WHO2005 = {
    "pm2.5": 10,
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
userinputs = Inputs("NW1 2DB", "WC1B 5EH")

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
graph = ox.graph_from_polygon(buffbox, network_type='walk', truncate_by_edge=False, retain_all=True)
fig, ax = ox.plot_graph(graph)

# ==========================================================================
# Drawing route between locations, check pollution values and redraw
# ==========================================================================


route = []
usernodes = userlocations.getnodes()
nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
pollution_status = False

while not pollution_status:

    route = nx.shortest_path(G=graph, source=usernodes[0], target=usernodes[1], weight='distance')
    route_nodes = nodes.loc[route]

    for index, row in route_nodes.iterrows():
        x_coord = row['x']
        y_coord = row['y']
        pm2_5 = obtainvalue(y_coord, x_coord, "pm2.5")
        pm10 = obtainvalue(y_coord, x_coord, "pm10")
        no2 = obtainvalue(y_coord, x_coord, "no2")
        # print("Break", pm2_5, pm10, no2)

        if index != usernodes[0] and index != usernodes[1]:

            if pm2_5 > WHO2005["pm2.5"] or pm10 > WHO2005["pm10"] or no2 > WHO2005["no2"]:
                graph.remove_node(index)
            else:
                pollution_status = True

fig, ax = ox.plot_graph_route(graph, route)
