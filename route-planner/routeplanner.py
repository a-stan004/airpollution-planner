# ==========================================================================
# 1.0 Importing packages, modules and scripts
# ==========================================================================

# Import networking packages, modules and errors
import osmnx as ox
from osmnx import routing
import networkx as nx
from networkx import NetworkXNoPath

# Import general geographical data packages
import geopandas as gpd
import pandas as pd
from geopy import Nominatim

# Import raster function from raster script
from raster import obtainvalue

# Import PyQt elements, folium and sys/io for UI
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QProgressBar, QRadioButton)
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt
import folium
import sys
import io


# ==========================================================================
# 2.0 Setting up PyQt UI class and building widgets
# ==========================================================================


class MyWindow(QWidget):
    """
    Window class for PyQt UI

    Attributes
        (self)

    Methods
        .__init___(): Constructs the window object
        .initwindow(): Sets title, size and defines global window variables
        .overallui(): Constructs the layout and widgets for the UI
        .selection(): Method which takes the input of the radio walk/cycle boxes and adds this to main script
        .runscript(): Rest of main script is housed here so it can be called as one within the window class

    """

    # Constructs window object, window attributes requiring change must be defined at __init__ in first instance
    def __init__(self):
        super().__init__(parent=None)
        self.input1_text = None
        self.input2_text = None
        self.radio_walk = None
        self.radio_cycle = None
        self.progress = None
        self.progress_label = None
        self.warning = None
        self.view = None
        self.legend1 = None
        self.legend2 = None
        self.legend3 = None
        self.legend4 = None
        self.legend5 = None
        self.legend6 = None
        self.legend7 = None
        self.legend8 = None
        self.distshortest = None
        self.distalt = None
        self.samepath = None
        self.initwindow()
        self.nettype = "walk"

    # Sets the size and title of box and calls the overallui method to construct widgets and layouts
    def initwindow(self):
        self.setWindowTitle(self.tr("Route Planner"))
        self.setMinimumSize(900, 1200)
        self.overallui()

    # Widgets and layouts constructed
    def overallui(self):

        # Logo at top of window
        logo1 = QLabel('London Plan')
        logo1.setStyleSheet('color: black; font-weight: bold; font-size: 20pt')
        logo2 = QLabel('AIR')
        logo2.setStyleSheet('color: darkgreen; font-weight: bold; font-size: 28pt; font-style: italic')

        # Description paragraph beneath logo
        description = QLabel('This tool allows you to plan lower pollution versions of your '
                             'normal walking or cycling routes. <br><br>'
                             'To start input your start and end locations. These can be in many formats such '
                             'as postcodes, street names, or even attractions such as Tower Bridge. Then '
                             'click FIND ROUTE. <br><br>'
                             'Hover over routes to see information. Pollution values are indicated '
                             'in the legend below. This tool currently only works for Greater London locations. Longer '
                             'routes may take a while to load - do not close the window even if '
                             'unresponsive for a while.')
        description.setStyleSheet('font-size: 7pt; font-weight: normal')
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)

        # Start and end input boxes
        input1_label = QLabel('Start:')
        input1_label.setStyleSheet('font-size: 9pt; font-weight: bold')
        self.input1_text = QLineEdit()
        input2_label = QLabel('End: ')
        input2_label.setStyleSheet('font-size: 9pt; font-weight: bold')
        self.input2_text = QLineEdit()

        # Radio buttons for walk or cycle selection
        self.radio_walk = QRadioButton("Walk", self)
        self.radio_walk.setStyleSheet('font-size: 9pt; font-weight: bold')
        self.radio_walk.setChecked(True)
        self.radio_cycle = QRadioButton("Cycle", self)
        self.radio_cycle.setStyleSheet('font-size: 9pt; font-weight: bold')
        # Connected to selection method which triggers when selection is made
        self.radio_walk.toggled.connect(self.selection)
        self.radio_cycle.toggled.connect(self.selection)

        # Run button triggers main script to be ran
        run_button = QPushButton('Find Route')
        run_button.setStyleSheet('font-size: 9pt; font-weight: bold; background-color: darkgreen; color: white')
        run_button.clicked.connect(self.runscript)

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress_label = QLabel('')
        self.progress_label.setAlignment(Qt.AlignCenter)

        # Error warning labels
        self.warning = QLabel('')
        self.warning.setStyleSheet('color: red; font-weight: normal')

        # View window for folium map
        self.view = QtWebEngineWidgets.QWebEngineView(parent=None)

        # Legend items, defined seperately to allow different colors
        self.legend1 = QLabel('<10')
        self.legend1.setStyleSheet('background-color: #40b81c; color: black')
        self.legend2 = QLabel('<20')
        self.legend2.setStyleSheet('background-color: #d1d119; color: black')
        self.legend3 = QLabel('<30')
        self.legend3.setStyleSheet('background-color: #d1a619; color: black')
        self.legend4 = QLabel('<40')
        self.legend4.setStyleSheet('background-color: #d14419; color: black')
        self.legend5 = QLabel('<50')
        self.legend5.setStyleSheet('background-color: #9c1919; color: white')
        self.legend6 = QLabel('<60')
        self.legend6.setStyleSheet('background-color: #3d0101; color: white')
        self.legend7 = QLabel('60+')
        self.legend7.setStyleSheet('background-color: #000000; color: white')
        self.legend8 = QLabel('µg/m3')

        # Route distance labels and warning message if routes are the same
        self.distshortest = QLabel('')
        self.distalt = QLabel('')
        self.samepath = QLabel('')

# ==========================================================================
# 3.0 Setting up PyQt UI layout
# ==========================================================================

        # Layout setup
        # Vertical box
        vbox = QVBoxLayout()
        # Horizontal sections
        logo = QHBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        hbox5 = QHBoxLayout()

        # Adding widgets section layouts
        logo.addWidget(logo1)
        logo.addWidget(logo2)

        hbox1.addWidget(input1_label)
        hbox1.addWidget(self.input1_text)

        hbox2.addWidget(input2_label)
        hbox2.addWidget(self.input2_text)

        hbox3.addWidget(self.radio_walk)
        hbox3.addWidget(self.radio_cycle)
        hbox3.setSpacing(20)
        hbox3.setAlignment(Qt.AlignCenter)

        hbox4.addWidget(self.distshortest)
        hbox4.addWidget(self.distalt)
        hbox4.setSpacing(20)
        hbox4.setAlignment(Qt.AlignCenter)

        hbox5.addWidget(self.legend1)
        hbox5.addWidget(self.legend2)
        hbox5.addWidget(self.legend3)
        hbox5.addWidget(self.legend4)
        hbox5.addWidget(self.legend5)
        hbox5.addWidget(self.legend6)
        hbox5.addWidget(self.legend7)
        hbox5.addWidget(self.legend8)

        # Vertical box overall construction
        vbox.addLayout(logo)
        logo.setSpacing(0)
        logo.setAlignment(Qt.AlignCenter)
        vbox.addWidget(description)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.warning)
        vbox.addLayout(hbox3)
        vbox.addWidget(run_button)
        vbox.addWidget(self.progress)
        vbox.addWidget(self.progress_label)
        vbox.addWidget(self.view)
        vbox.setStretchFactor(self.view, 1)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox4)
        vbox.addWidget(self.samepath)
        vbox.setSpacing(20)

        # Hiding unneeded start elements
        self.progress_label.hide()
        self.progress.hide()
        self.warning.hide()
        self.setLayout(vbox)

    def selection(self):
        """
        Checks which radio button is selected and changes global window variable
        This means the osmnx graph will choose the correct transport choice

        Attributes
            (self)

        Methods
            (none)

        """

        if self.radio_walk.isChecked():
            self.nettype = "walk"
        elif self.radio_cycle.isChecked():
            self.nettype = "bike"
        else:
            self.nettype = "walk"

# ==========================================================================
# 4.0 Running low-pollution route finder script
# ==========================================================================

    def runscript(self):
        """
        Runs the main script which results in a folium route map being contructed

        Classes
            Inputs: User inputs for start and end locations
            Locations: Route class, with start, end, lat, long information

        Attributes
            (self)

        Methods
            checkboundary(): Checks if coordinates are within the Greater London boundary
            limitervalues(): Defines allowable air pollution limits for route calculation
            geolocation(): Takes a node as input and returns x, y values
            get_geo_data(): Gathers pollution data for nodes using obtainvalue raster function
            compare(): Compares node pollution values to limits
            good_node(): Checks if a node is within limits
            process_path(): Checks all the nodes in a route for nodes exceeding limits
            restricted_path(): Tries to construct a route with high pollution value nodes removed
            edgepollution(): Creates index of pollution and adds to graph edges
            colorpicker(): Chooses color based on pollution value
            drawfig(): Constructs a folium map of routes

        """

# ==========================================================================
# 4.1 Getting user inputs and geocoding locations
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
                Constructs all the necessary attributes for the inputs object.

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

        # Get inputs from PyQt input boxes
        start = self.input1_text.text()
        end = self.input2_text.text()
        # Creates class instance of Inputs with two user inputs
        userinputs = Inputs(start, end)

        geo_initial = userinputs.geocodeaddresses()[0]
        geo_target = userinputs.geocodeaddresses()[1]

        # If geocoding returns a fail from the try/except block warning is displayed
        if geo_initial == 'Fail' and geo_target == 'Fail':
            self.warning.setText('One or more addresses could not be located')
            self.warning.show()
            self.input1_text.setText("")
            self.input2_text.setText("")
            return

        def checkboundary(geocodedinital, geocodedtarget):
            """
            Takes a latitude and longitude and checks whether it is in the Greater London boundary
            This is done by sampling the raster and checking for 0 or Null values

            Args
                geocodedinital (list): Input class style list with location, latitude, longitude of start location
                geocodedtarget (list): Input class style list with location, latitude, longitude of end location

            Returns
                in_london (bool): True or false of whether location is within Greater London boundary
            """
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

        # If Greater London check returns False then a warning is displayed
        if not in_london_status:
            self.warning.show()
            self.warning.setText('One or more locations outside of Greater London boundary')
            return

# ==========================================================================
# 4.2 Processing initial fastest route
# ==========================================================================

        # Hiding warnings and starting progress bar
        self.warning.hide()
        self.progress_label.show()
        self.progress.show()
        self.progress_label.setText('Locating start and end points...')
        self.progress.setValue(20)
        self.samepath.hide()

        class Locations:
            """
            Class representing users locations, capable of producing geodataframes and nodes
            Attributes easiest constructed using Nomantim tool within the Inputs class

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

        # Updating progress bar
        self.progress.setValue(50)
        self.progress_label.setText('Drawing route between locations')

        # Variable created to store the geopandas data frame
        gdf = userlocations.gpdframe()
        # Creating a polygon of the search area and buffering it so that routes are not limited
        box = gdf.unary_union.envelope
        buffbox = box.buffer(0.01)

        # Drawing graph of buffered area with correct transport type
        graph = ox.graph_from_polygon(buffbox, network_type=self.nettype, truncate_by_edge=False, retain_all=True)
        # Getting location nodes and drawing initial route
        usernodes = userlocations.getnodes()

        # If inital route cannot be drawn an error message is displayed
        try:
            route = nx.shortest_path(G=graph, source=usernodes[0], target=usernodes[1], weight="distance")
        except NetworkXNoPath:
            self.warning.show()
            self.warning.setText("Unable to draw a route between locations, check addresses and retry")
            self.progress.hide()
            self.progress_label.hide()
            return

        # Gathering route length and rounding to 2 decimal places
        shortest_edges = ox.routing.route_to_gdf(graph, route)
        shortest_length = sum(shortest_edges['length'])
        shortest_length_round = round((shortest_length / 1000), 2)

# ==========================================================================
# 4.3 Finding lower pollution route
# ==========================================================================
        def limitervalues():
            """
            Returns a tuple of three values used as pollution limits
            Allows one place to change values rather than constant redefinition

            Args
                (none)

            Returns
                chosenlimits (tuple): Tuple of PM2.5, PM10 and NO2 values

            """

            # Safe limits for air pollution - World Health Organisation
            who2005 = {
                "pm2_5": 10,
                "pm10": 20,
                "no2": 40
            }
            pm2_5value = float(who2005["pm2_5"])
            pm10value = float(who2005["pm10"])
            no2value = float(who2005["no2"])
            chosenlimits = (pm2_5value, pm10value, no2value)
            return chosenlimits

        # Defining limits and initial tolerance
        limits = limitervalues()
        tolerance = 1

        # Setting up a location to store pollution values that are high
        geo_cache = {}

        # Converting graph into geodataframe
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

        # Update progress bar
        self.progress.setValue(70)
        self.progress_label.setText('Checking pollution along route')

        # Attempts to make a valid path
        valid_path = process_path(route)

        # Blank attempt to add nodes to
        attempt = []

        # Where no valid path, while loop reattempts route by resetting bad nodes and upping limit tolerances
        while not valid_path:
            attempt = restricted_path(graph)
            if not attempt:
                tolerance *= 1.5
                bad_nodes = set()
            else:
                valid_path = process_path(attempt)

        # Gathering route length and rounding to 2 decimal places
        alt_edges = ox.routing.route_to_gdf(graph, attempt)
        alt_length = sum(alt_edges['length'])
        alt_length_rounded = round((alt_length / 1000), 2)

# ==========================================================================
# 4.4 Styling routes based on pollution
# ==========================================================================

        def edgepollution(figgraph, figroute):
            """
            Takes a route and its associated graph, and returns an edge index of pollution based on three pollutants
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

        # Update progress bar
        self.progress.setValue(80)
        self.progress_label.setText('Drawing routes')

        # Getting edge colors
        edges_values = edgepollution(graph, route)
        alt_edges_values = edgepollution(graph, attempt)

        def colorpicker(value):
            """
            Takes float and returns a color from green to red to black scale based on how high the integer is

            Args
                value (float): Pollution edge value

            Returns
                color (string): Hexcode of color

            """

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
                m (map) (.html): Saves a html file of final route
            """
            originedges = ox.routing.route_to_gdf(foliumgraph, foliumroute['edges'], weight='length')
            originedges['value'] = foliumroute['values']

            alternateedges = ox.routing.route_to_gdf(foliumgraph, foliumalt['edges'], weight='length')
            alternateedges['value'] = foliumalt['values']

            if shortest_length_round > 12:
                zoom = 11
            elif shortest_length_round > 10:
                zoom = 12
            elif shortest_length_round > 5:
                zoom = 13
            else:
                zoom = 14

            center = [((float(geo_initial[1]) + float(geo_target[1])) / 2),
                      ((float(geo_initial[2]) + float(geo_target[2])) / 2)]
            m = folium.Map(
                location=center,
                zoom_start=zoom,
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

        # Draw and temporarily save map
        folmap = drawfig(graph, edges_values, alt_edges_values, geo_initial, geo_target)
        data = io.BytesIO()
        folmap.save(data, close_file=False)

        # Write saved map to view window in UI
        self.view.setHtml(data.getvalue().decode())

        # Hide progress bar and display distances and warning if routes are the same
        self.progress_label.hide()
        self.progress.hide()
        self.distshortest.show()
        self.distshortest.setText(f'Shortest Path: {shortest_length_round}km')
        self.distalt.show()
        self.distalt.setText(f'Alternative Path: {alt_length_rounded}km')
        if alt_length == shortest_length:
            self.distalt.hide()
            self.distshortest.hide()
            self.samepath.show()
            self.samepath.setText('No identifiable lower pollution path. Pollution along route is low.')


# ==========================================================================
# 5.0 Running the application
# ==========================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
