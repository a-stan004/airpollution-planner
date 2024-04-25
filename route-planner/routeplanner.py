import osmnx as ox
from osmnx import routing
import networkx as nx
import geopandas as gpd
import pandas as pd
from geopy import Nominatim
from networkx import NetworkXNoPath
from raster import obtainvalue
import folium
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QProgressBar)
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt
import io
import sys

# ==========================================================================
# Setting up UI classes
# ==========================================================================


class MyWindow(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.initwindow()

    def initwindow(self):
        self.setWindowTitle(self.tr("MAP PROJECT"))
        self.setMinimumSize(750, 750)
        self.overallui()

    def overallui(self):

        input1_label = QLabel('Start:')
        self.input1_text = QLineEdit()
        input2_label = QLabel('End:')
        self.input2_text = QLineEdit()

        run_button = QPushButton('Find Route')
        run_button.clicked.connect(self.runscript)

        self.progress = QProgressBar(self)
        self.progress.setAlignment(Qt.AlignCenter)

        self.warning = QLabel('')

        self.input3_label = QLabel('')
        self.input3_label.setAlignment(Qt.AlignCenter)

        self.view = QtWebEngineWidgets.QWebEngineView(parent=None)

        # Layout setup
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()

        hbox1.addWidget(input1_label)
        hbox1.addWidget(self.input1_text)

        hbox2.addWidget(input2_label)
        hbox2.addWidget(self.input2_text)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.warning)
        vbox.addWidget(run_button)
        vbox.addWidget(self.progress)
        vbox.addWidget(self.input3_label)
        vbox.addWidget(self.view)
        vbox.setStretchFactor(self.view, 1)
        vbox.setSpacing(5)

        self.input3_label.hide()
        self.progress.hide()
        self.warning.hide()
        self.setLayout(vbox)

# ==========================================================================
# Gathering inputs and geocoding
# ==========================================================================

    def runscript(self):
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
                targetloc = loc.geocode(self.target)
                try:
                    geocodeinit = [initloc.address, initloc.latitude, initloc.longitude]
                    geocodetarget = [targetloc.address, targetloc.latitude, targetloc.longitude]
                except AttributeError:
                    geocodeinit = "Fail"
                    geocodetarget = "Fail"
                    return geocodeinit, geocodetarget
                return geocodeinit, geocodetarget


        start = self.input1_text.text()
        end = self.input2_text.text()
        # Creates class instance of Inputs with two user inputs
        userinputs = Inputs(start, end)

        geo_initial = userinputs.geocodeaddresses()[0]
        geo_target = userinputs.geocodeaddresses()[1]

        if geo_initial == 'Fail' and geo_target == 'Fail':

            self.warning.setText('One or more addresses could not be located')
            self.warning.show()
            self.input1_text.setText("")
            self.input2_text.setText("")
            return

        def checkboundary(geocodedinital, geocodedtarget):
            init_latlong = geocodedinital[-2], geocodedinital[-1]
            target_latlong = geocodedtarget[-2], geocodedtarget[-1]
            if (obtainvalue(init_latlong[0], init_latlong[1], 'no2') == 0 or None or
                    obtainvalue(target_latlong[0], target_latlong[1], 'no2') == 0 or None):
                in_london = False
                return in_london
            else:
                in_london = True
                return in_london

        in_london_status = checkboundary(geo_initial, geo_target)

        if not in_london_status:
            self.warning.show()
            self.warning.setText('One or more locations outside of Greater London boundary')
            return

        self.warning.hide()
        self.input3_label.show()
        self.progress.show()
        self.input3_label.setText('Locating start and end points...')
        self.progress.setValue(20)




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


        # Get initial limiter values
        def limitervalues():
            # Safe limits for air pollution 2005 WHO
            who2005 = {
                "pm2_5": 10,
                "pm10": 20,
                "no2": 40
            }
            pm2_5value = float(who2005["pm2_5"])
            pm10value = float(who2005["pm10"])
            no2value = float(who2005["no2"])
            limits = (pm2_5value, pm10value, no2value)
            return limits

        self.progress.setValue(50)
        self.input3_label.setText('Drawing route between locations')

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

        try:
            route = nx.shortest_path(G=graph, source=usernodes[0], target=usernodes[1], weight="distance")
        except NetworkXNoPath:
            self.warning.show()
            self.warning.setText("Unable to draw a route between locations, check addresses and retry")
            self.progress.hide()
            self.input3_label.hide()
            return

        limits = limitervalues()
        tolerance = 1

        # Set up a location to store pollution values that are high
        geo_cache = {}

        # Take graph and make it into a geodataframe
        geo_data = ox.graph_to_gdfs(graph, nodes=True, edges=False)


        # Unordered sets created to store nodes
        all_nodes = set(graph.nodes())
        bad_nodes = set()


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

        self.progress.setValue(70)
        self.input3_label.setText('Checking pollution along route')

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

        # Coloring of routes and drawing to folium
        def edgepollution(figgraph, figroute):
            """
            Takes a route and its associated graph, and returns an index of pollution based on three pollutants for each edge
            Requires obtainvalue() script from raster.py

            Args
                figgraph (MultiDiGraph): OSMnx pre-built graph as input
                figroute (list): OSMnx list of node values constructed using routing module
            Returns
                route_values (dict):
                    'edges': Edge number
                    'values': Pollutant index
            """
            edges = ox.routing.route_to_gdf(figgraph, figroute, weight='length')
            nodes = ox.graph_to_gdfs(figgraph, nodes=True, edges=False)
            edges.sort_index(inplace=True)
            for index, edge in edges.iterrows():
                node1num = index[0]
                node2num = index[1]
                node1 = nodes.loc[node1num]
                node2 = nodes.loc[node2num]
                n1v1 = obtainvalue(node1['y'], node1['x'], 'PM2.5')
                n1v2 = obtainvalue(node1['y'], node1['x'], 'PM10')
                n1v3 = obtainvalue(node1['y'], node1['x'], 'NO2')
                node1avg = (n1v1 + n1v2 + n1v3) / 3
                n2v1 = obtainvalue(node2['y'], node2['x'], 'PM2.5')
                n2v2 = obtainvalue(node2['y'], node2['x'], 'PM10')
                n2v3 = obtainvalue(node2['y'], node2['x'], 'NO2')
                node2avg = (n2v1 + n2v2 + n2v3) / 3
                edges.loc[(node1num, node2num), 'avgvalue'] = (node1avg + node2avg) / 2
                route_values = {'edges': figroute, 'values': edges['avgvalue'].tolist()}
            return route_values


        self.progress.setValue(90)
        self.input3_label.setText('Drawing routes')

        edges_values = edgepollution(graph, route)
        alt_edges_values = edgepollution(graph, attempt)

        self.progress.setValue(80)
        self.input3_label.setText('Finding lower pollution route')

        def colorpicker(value):
            if value < 10:
                color = "#40b81c"
            elif value < 20:
                color = "#d1d119"
            elif value < 30:
                color = "#d1a619"
            elif value < 40:
                color = "#d14419"
            elif value < 50:
                color = "#9c1919"
            elif value < 60:
                color = "#3d0101"
            else:
                color = "#000000"
            return color


        def drawfig(foliumgraph, foliumroute, foliumalt, initial, target):
            """
            Takes two routes and their associated graph, and constructs a folium map
            Requires obtainvalue() script from raster.py

            Args
                figgraph (MultiDiGraph): OSMnx pre-built graph as input
                figroute (list): OSMnx list of node values constructed using routing module
            Returns
                map (.html): Saves a html file of final route
            """
            originedges = ox.routing.route_to_gdf(foliumgraph, foliumroute['edges'], weight='length')
            originedges['value'] = foliumroute['values']

            alternateedges = ox.routing.route_to_gdf(foliumgraph, foliumalt['edges'], weight='length')
            alternateedges['value'] = foliumalt['values']

            center = [((float(geo_initial[1])+float(geo_target[1]))/2),
                      ((float(geo_initial[2])+float(geo_target[2]))/2)]
            m = folium.Map(
                location=center,
                zoom_start=14,
                tiles="cartodb positron",
                opacity=1
            )

            for index, edge in originedges.iterrows():
                value = edge['value']
                color = colorpicker(value)
                origincoordinates = edge['geometry'].coords.xy
                origincoord_tuples = list(zip(origincoordinates[1], origincoordinates[0]))

                folium.PolyLine(
                    locations=origincoord_tuples,
                    color=color,
                    weight=10,
                    opacity=1,
                    tooltip="Fastest Route"
                ).add_to(m)

            for index_alt, edge_alt in alternateedges.iterrows():
                value = edge_alt['value']
                color = colorpicker(value)
                altcoordinates = edge_alt['geometry'].coords.xy
                altcoord_tuples = list(zip(altcoordinates[1], altcoordinates[0]))

                folium.PolyLine(
                    locations=altcoord_tuples,
                    color=color,
                    weight=10,
                    opacity=1,
                    tooltip="Lower Pollution Alternative"
                ).add_to(m)

            folium.Marker(
                location=[initial[1], initial[2]],
                tooltip='Start',
                icon=folium.Icon(color='green')
            ).add_to(m)

            folium.Marker(
                location=[target[1], target[2]],
                tooltip='End',
                icon=folium.Icon(color='green')
            ).add_to(m)

            return m

        folmap = drawfig(graph, edges_values, alt_edges_values, geo_initial, geo_target)
        print("folmap achieved")
        data = io.BytesIO()
        folmap.save(data, close_file=False)
        print("folmap saved")
        self.view.setHtml(data.getvalue().decode())
        self.input3_label.hide()
        self.progress.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())







