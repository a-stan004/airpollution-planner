import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from geopy import Nominatim
from shapely.geometry import box

# ==========================================================================
# Gathering inputs and geocoding
# ==========================================================================

# Variables created to store placenames
initalplace = "WS79LQ"
targetplace = "WS79JP"


# Address locator is set up to geocode locations using geopy nominatim
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


geo_inital = geocodeaddresses(initalplace)
geo_target = geocodeaddresses(targetplace)


# ==========================================================================
# Constructing a graph for the area
# ==========================================================================

# Puts the locations into a pandas dataframe
df = pd.DataFrame(
    {
        "Place": [geo_inital[0], geo_target[0]],
        "Latitude": [geo_inital[1], geo_target[1]],
        "Longitude": [geo_inital[2], geo_target[2]],
    }
)
# Converting to a geopandas dataframe to add a shapely geometry
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
)

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


orig_node = ox.nearest_nodes(graph, geo_inital[2], geo_inital[1])
target_node = ox.nearest_nodes(graph, geo_target[2], geo_target[1])

route = nx.shortest_path(G=graph, source=orig_node, target=target_node, weight='distance')
fig, ax = ox.plot_graph_route(graph, route)

# ==========================================================================
# Gathering locations of nodes along route and checking pollution values
# ==========================================================================

nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
route_nodes = nodes.loc[route]




