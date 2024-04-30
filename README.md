![Logo](/guide_images/logo.PNG)

# Introduction
A route planner for London cyclists with a specific focus on avoiding high pollution hotspots. Written in Python 3.2 using a PyQt GUI. Ulster University EGM722 Module Assessment.

## Contents
- [Installation](#installation)
    - [Cloning the repository](#cloning-the-repository)
    - [Setting up the environment](#setting-up-the-environment)
- [Script Breakdown](#script-breakdown)
- [Example Usage](#example-usage)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Installation
### Forking the repository
> [!NOTE]
> This assumes you have already set up git and github. More information about how to do this can be found [here](https://docs.github.com/en/get-started/getting-started-with-git/set-up-git).

1. On the repository homepage, select the fork option (**Figure 1**)

2. Unselect 'main only' and click 'create fork'

![Forking the repo](/guide_images/forkingtherepo.PNG)
**Figure 1 - Forking the repository on GitHub.com**

### Cloning the repository
This can be done via the command line or through GitHub Desktop. 

**Command Line**
1. To clone the repository to your machine with the command line use the code
```
git clone https://github.com/a-stan004/airpollution-planner
```

**GitHub Desktop**
1. To use GitHub Desktop, first sign in to your GitHub account
2. Select the repository from the list on the homepage. If it is not present, instead navigate to *File > Clone Repository*  and select the repository from there (**Figure 2**). 
3. Click Clone.

![Cloning the repo](/guide_images/cloningtherepo.PNG)
**Figure 2 - Cloning repository on GitHub Desktop**

### Setting up the environment
> [!NOTE]
> This assumes you have already set up conda and Anaconda Navigator. More information about how to do this can be found [here](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html).

An [environment file](airpollutionenvironment.yml) is included within the repository. This can be run through the command line or through Anaconda Navigator.

**Command Line**
1. Open the command line and enter the below code, replace your path with your directory where the yml is stored.
```
conda env create -f yourpath/airpollutionenvironment.yml
```
2. Activate the environment, the name will be airpollutionenvironment unless you have changed it.
```
conda activate airpollutionenvironment
```
3. Verify this has been successful by listing the loaded packages
```
conda env list
```

**Anaconda Navigator**
1. Open Anaconda Navigator and go to the Environments tab
2. Select Import
3. Choose the .yml file from your machine and select import (**Figure 3**)

![Importing environment](/guide_images/anaconda.PNG)
**Figure 3 - Importing the environment on Anaconda Navigator**

If conda is not your preferred method of installation all packages are also available using pip, and are detailed below.

### Package List
> [!TIP]
> Select a package below to view its documentation

*Routing packages*
- [OSMnx](https://osmnx.readthedocs.io/en/stable/getting-started.html)
- [NetworkX](https://networkx.org/documentation/stable/index.html)

*Data storage packages*
- [GeoPandas](https://geopandas.org/en/stable/index.html)
- [Pandas](https://pandas.pydata.org/)

*Location Identification*
- [GeoPy](https://geopy.readthedocs.io/en/stable/)
- [Rasterio](https://rasterio.readthedocs.io/en/stable/)

*GUI*
- [PyQt](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Folium](https://python-visualization.github.io/folium/latest/)


**The repository is now ready to be run!**

## Script Breakdown
> [!TIP]
> The script is broken up into sections commented in the script from 1.0 to 5.0. The breakdown will refer to these numbers throughout.

There are two scripts within the repository. The raster.py script is only required if wishing to modify the raster. The routeplanner.py script is the main script which runs to produce the tool. It integrates the raster.py script without needing to access it directly.

> [!NOTE]
> The following script breakdown assumes you have set up the git repository and have opened the routeplanner.py script in your preferred integrated development environment (IDE) such as [PyCharm](https://www.jetbrains.com/pycharm/) or [Visual Studio Code](https://visualstudio.microsoft.com/vs/community/).

### 1.0 Importing packages, modules and scripts

Firstly, the relevant packages are imported. OSMnx was chosen as the network analyst package due to its excellent results in numerous studies (Boeing 2017; 2018; Alattar *et al*. 2021). The package is based off the NetworkX package hence its inclusion in the package list, and builds street networks using OpenStreetMap. This allows for street networks adequate for complex route planning to be created by the script. The use of geographical data such as nodes (points) and (edges) means an adequate storage method is required, hence the use of geopandas. This is a well-established data type, and is integrated into OSMnx functions, allowing for easy data manipulation. 

Gathering user inputs and interpreting these into geographical locations, such that the user does not have to enter in a speicifc format is tricky. The method chosen for this tool is the Nominatim tool within the GeoPy package. This tool has been used in other studies and provides adequate locational accuracy (Serene *et al*. 2023; Clemens 2015). Although, the tool will often choose the first item that matches the input rather than the most relevant, requiring more specific input. E.g. Camden, New Jersey is returned until Camden, London is specified.

To provide the pollution data, an API was preferable, however no API with a resolution high enough for street by street measurement was available free-to-use. Previous commits demonstrate the addition of OpenWeatherMap API (OpenWeatherMap 2024) but this 11km resolution is unsuitable for shorter routes. The final solution is to use rasters to provide the air pollution data. This requires high confidence in the raster, hence, a reliable data source is required. Many UK raster maps use interpolation to such a high level they are unsuitable. London Datastore, a site provided by the Mayor of London's Office, provides a raster of projected pollution for 2025, which uses data from live sensors all over the city. These can be obtained from the Detailed Road Transport section of the London Atmospheric Emissions Inventory (2019), located [here](https://data.london.gov.uk/dataset/london-atmospheric-emissions-inventory--laei--2019). Data for various other years, past and present is also available which could be easily implemented into the raster script (more thoroughly discussed in [Section 4.3](#43-finding-lower-pollution-route)). Rasterio is used to sample these raster maps based on the latitude and longitude of OSMnx nodes to return pollution values along routes. The downside is the tool, in its unmodified state can only be used for the areas it is provided rasters for, currently Greater London.

Finally, it was deemed important for the user to have access to the tool in a way that required no coding knowledge, to the extent of simply pressing run. This allows anyone to be able to follow the above steps and access the tool.

An executable file to accompany the script would have been prefereable to bypass installation and code altogether. However, due to a bug with PyInstaller when used with Rasterio, this is currently difficult without modification of the package - which would have to happen at the user end to avoid a large amount of additional repositorial code. Py2Exe was also deemed excessive as the user would be required to have Microsoft Visual C Runtime DLL, which could not be guaranteed. The final solution is simply to run the script in any IDE and generate a PyQt Graphical User Interface (GUI). PyQt is chosen due to its inclusion in conda without additional channels, as would be required for the main alternative, the more deprecated in terms of modern UI - TKinter.

Maps displayed in PyQt are generated using Folium. Interactive maps are needed so that the user can zoom and analyse their routes, hence packages such as Cartopy are not suitable. Folium was chosen over popular alternative mapboxjs. Although both are based off JavaScript library leafletjs, Folium's ability to function without an authentication token makes it preferable (Earth Data Science 2024).

### 2.0 Setting up PyQt UI class and building widgets

For the code to be executed within a GUI the PyQt window class must first be set up. The structure of this is illustrated in **Figure 4**.

![PyQt Layout](/guide_images/layout.PNG)
**Figure 4 - PyQt Structure**

PyQt operates using slots and signals. This is demonstrated in **Figure 5**. The button widget can have a signal attached to it, which when toggled such as with the click signal of the button, triggers the event of the built-in 'slot' of the button.

![Slots and Signals](/guide_images/signalsandslots.PNG)
**Figure 5 - PyQt Slots and Symbols Structure**

As demonstrated, first a Window class must be created. This is performed in the code on line 34:
```
class MyWindow(QWidget):
```
Within this, the __init__ function initialises the dynamic QWidget names, so that they can be used in the overallui() function. The initwindow() function beginning on Line 76, sets up the window before calling the overallui() function.

The remaining code in this section establishes a series of widgets using QLabel, QInput, QRadioButton, QProgressBar and QWebEngineView. More information about these widgets can be found [here](https://doc.qt.io/qtforpython-6/overviews/gallery.html). 

The most important widget is the Find Route button, which when clicked triggers the main route finding script which underpins the tool.
```
run_button = QPushButton('Find Route')
run_button.clicked.connect(self.runscript)
```

### 3.0 Setting up PyQt UI layout

Following the PyQt structure, a layout is required to house the widgets. This is setup in lines 168 - 229. A vertical box is created and added to it are a number of horizontal 'rows', alongside standalone widgets such as the QWebEngineView. Inline styling is applied throughout using code such as the below lines:
```
self.widgetname.setStyleSheet('background-color: hex; color: hex'')
self.widgetname.setAlignment(Qt.AlignChoice)
```

The selection function is required to make the radio buttons function, so that the user can choose a transport choice. This simply checks the button status and if unchanged returns 'walk', or 'bike' if selected.

The final initial layout of the GUI is shown in **Figure 6**.

![PyQt GUI](/guide_images/initialui.PNG)
**Figure 6 - PyQt Initial GUI**

### 4.0 Running low-pollution route finder script

The runscript() function has to be executed as one so that it is easily callable from the PyQt button widget. Therefore for ease, it has been further broken up into 4.1, 4.2 etc., shown throughout the code. It is also worth noting that the code is fully annotated with comments and docstrings throughout to assist understanding without having to refer back to this documentation.

#### 4.1 Getting user inputs and geocoding locations

Start and end locations from the PyQt inputs are stored in the Inputs class, which takes in an inital and target location. The method geocodeaddresses (Line 314) then attempts to geolocate both locations using the Nominatim tool. A try/except block (Line 329) catches the Attribute error if the Nomantim fails. The user is then served a warning that they must retry locations (Line 348, **Figure 7**).

![Error Location](/guide_images/errorlocation.PNG)
**Figure 7 - Location error in GUI**

Due to the raster restrictions outlined in [Section 1.0](#10-importing-packages-modules-and-scripts) the locations must also be checked for whether they are in the boundary. The checkboundary() function checks whether a 0 or Null is returned (Line 355), and returns a booleon. If false this also returns a warning (Line 380, **Figure 8**). Refer to the checkboundary() docstring for more information on this.

![Error Boundary](/guide_images/errorboundary.PNG)
**Figure 8 - Boundary error in GUI**

#### 4.2 Processing inital fastest route

The progress bar is first triggered at the start of this section to provide the user with updates on their request. This is done manually with numbers taken as a parameter of the QProgressBar widget, e.g. 20(%). 

A new class is constructed here known as Locations. the objective of this class is to make it easier to house data in the correct format for route handling. Designed to follow the Nominatim step within Inputs, the inputs are locations, latitudes and longitudes (the output of the Nominatim tool). See Line 467 for details of formatting data for input into the Locations class.

The Locations class functions are designed to create a geopandas data frame for use in OSMnx graph construction, and get nodes for use in OSMnx routing.

OSMnx creates network 'graphs' consisting of nodes and edges. The creation of the inital graph is done in Lines 503-509 or as follows.

```
gdf = userlocations.gpdframe()
box = gdf.unary_union.envelope
buffbox = box.buffer(0.01)
graph = ox.graph_from_polygon(buffbox, network_type=self.nettype, truncate_by_edge=False, retain_all=True)
```

To ensure a large enough graph is created a buffer box is created. Wihtout this, longer routes avoiding parts of the graph are at risk of being cut off and therefore unidentifiable. A buffer of 0.01 was chosen, which has was tested to provide a sufficient balance between speed of processing and size of graph.

A sample graph is shown in **Figure 9**.

![Sample Graph](/guide_images/samplegraph.PNG)
**Figure 9 - Graph created using OSMnx showing nodes and edges**


The try/except block in Line 515 then attempts to route between the user nodes. Where this is not possible and a NetworkXNoPath error is produced, this is caught and an error returned, rather than crashing the GUI. The route code is as follows and produces a list of nodes from the graph.

```
route = nx.shortest_path(G=graph, source=usernodes[0], target=usernodes[1], weight="distance")
```

Distance calculation is performed on Lines 524-526 or as follows. This produces a value in kilometers for the route by converting the route to a geodataframe, summing its edges and rounding the value - displayed later in the GUI.

```
shortest_edges = ox.routing.route_to_gdf(graph, route)
shortest_length = sum(shortest_edges['length'])
shortest_length_round = round((shortest_length / 1000), 2)
```

#### 4.3 Finding lower pollution route

The method for making a lower pollution route is shown in the flowchart below (**Figure 10**). 

![Flowchart](/guide_images/flowchart.PNG)
**Figure 10 - Lower pollution route finder flowchart**

The limitervalues() function provides a single place that limits are defined so that the values can be adjusted for different objectives. Limits are defined for PM2.5, PM10 and NO2, the most prevalent and harmful pollutants in London.

> [!NOTE]
> The raster script is located within the repository. To change rasters, the obtainvalue() function should be modified, after the rasters have been added to the data folder. If pollutants are changed then the limitervalues() function needs to be modified also. 

A tolerance value is set to 1 to begin, so it does not modify the limits. All route nodes are checked against the raster, where they exceed the limits set for any pollutant they are removed from the graph. The route is then redrawn if possible. Where this is not possible, all nodes are put back and the tolerance is increased by 50%. This value was chosen to provide a good balance between speed of processing and being able to provide realistic lower pollution value routes. The process then repeats until a new route is found. In some cases, if values are below limits already, the routes are the same. The user is informed of this with a message in the GUI (Lines 831-835).

The flowchart code runs from lines 532-657. Six functions are used to make the process.

- getlocation() - Locates the nodes x and y coordinates
- getgeodata() - Gets pollution data for nodes
- compare() - Compares node pollution data to limits
- goodnode() - Returns true if limits are not exceeded
- processpath() - Checks if all route nodes are 'good nodes'
- restrictedpath() - Route construction function with allowed nodes

Route distance is also collected from the route in the same method as [Section 4.2](#42-processing-inital-fastest-route).

#### 4.4 Styling routes based on pollution

In this section routes are styled and exported to a folium map. The function edgepollution() takes a graph and route as input and iterates through the edges between nodes to make an index of pollution values for each.

*Index = (NO2 + PM2.5 + PM10) / Number of values*

This index of average pollution is then used in the colorpicker()function to hoose a color for each edge in the folium map.

The drawfig() function requires both routes and the initial graph used to draw the fastest route (with no nodes removed). A geodataframe is created with the pollution value for each edge. Lines 756-766 set out the inital zoom based on fastest route length and centre point based on start and end points. This ensures the route is always central and comprehensively displayed on the screen, regardless of length. CartoDB Positron is chosen as the basemap due to its neutral colours, making the routes more easily visible. A for loop on line 774 the itterates through all edges, colours them, and adds them to the map. Finally, markers are added (Lines 802-812) and the function returns the map.

The folium map is temporarily saved using *io.BytesIO()*. This allows the map to be drawn in the *view.setHtml* line. This operation is the reason for the inital *import io* statement.

```
folmap = drawfig(graph, edges_values, alt_edges_values, geo_initial, geo_target)
data = io.BytesIO()
folmap.save(data, close_file=False)
self.view.setHtml(data.getvalue().decode())
```

The final part of this section displays both routes distances by modifying GUI labels.

### 5.0 Running the application

The code to launch the application is as follows:

```
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
```

This checks that the code is being called from the main script it exists in, in this case routeplanner.py. A QApplication instance is created, which requires the *import sys* statement from [Section 1.0](#10-importing-packages-modules-and-scripts). Then the window is constructed from the MyWindow() class in [Section 2.0](#20-setting-up-pyqt-ui-class-and-building-widgets). By default the window is hidden so *window.show()* is required. The application should now launch.

> [!IMPORTANT]
> If the application does not launch please follow troubleshooting steps in [Troubleshooting](#troubleshooting).

## Example Usage

The Nomantim is capable of taking inputs such as landmarks, train stations, place names, or postcodes. Some examples are demonstrated below. Routes and points can be hovered over to see details.

>[!NOTE]
> If the *not responding* error is encountered, do not close the application and refer to [Troubleshooting](#troubleshooting)

1. ### Creating a short walking route between London Marylebone and London Paddington train stations (Figure 11)

![Test1](/guide_images/test1.PNG)
**Figure 11 - Walking route between London Marylebone and London Paddington**


The route has avoided several high pollution stretches of main road, creating a route with a pollution average of no higher than 30µg/m3, compared to the alternative of up to 50µg/m3. 

2. ### Creating a cycling route between London Marylebone and City of London (Figure 12)

![Test2](/guide_images/test2.PNG)
**Figure 12 - Cycling route between London Marylebone and City of London**

This route adds just over 1km of distance to the route, but avoids a significant stretch of high pollution near Fitzrovia.

3. ### Using postcodes to map a cycling route between two London museums (Figure 13)

![Test3](/guide_images/test3.PNG)
**Figure 13 - Cycling route between two postcodes**

This is another example with similar distance but many high pollution junctions and main roads avoided.

4. ### Using the tool to navigate between tourist landmarks (Figure 14)

![Test4](/guide_images/test4.PNG)
**Figure 14 - Walking route between two landmarks**

In this example, the routes are very similar, but nevertheless pollution has been lowered.

5. ### Using the tool for a very long distance route from Uxbridge to Woolwich (Figure 15)

![Test5](/guide_images/test5.PNG)
**Figure 15 - Cycling route from Uxbridge to Woolwich**

Whilst taking longer than other routes to process, the tool is capable of routes of more than 50km in length. 

6. ### Demonstrating the progress bar with a short route

A route such as Ealing to Ealing Broadway is recommended as the route is quick to render and demonstrates the progress bar quickly.

## Troubleshooting

### One or more locations could not be located error message

The Nominatim tool has failed to find a location which matches one of the user inputs. Check spelling and if certain location is spelt correctly, try adding ', London' afterwards. This eliminates global locations being used.

### One or more locations is outside of Greater London Boundary error message

Check that the location is definitely within the Greater London boundary (roughly the M25). If certain the location is within this boundary, try adding ', London' afterwards. This ensures the correct location is used. If this fails, try using postcodes, these are highly likely to be recognised.

### Unable to draw route between locations error message

Due to the tools reliance on OpenStreetMap, occasionally locations cannot be accurately located, resulting in this error. For example, locations near bridges and water may not be recognised as reachable. Where this occurs, attempt using a nearby landmark or postcode to the location required.

### Tool crashes and ModuleError in console

Enusure that airpollutionenvironment.yml is loaded correctly by following the steps in [Setting up the environment section](#setting-up-the-environment). Check that the lines of code in [Section 1.0 Importing packages and modules](#10-importing-packages-modules-and-scripts) are correct and have not been accidently modified. 

### Tool crashes and AttributeError in console

This is usually caused by errors in the Nominatim tool. These should be caught in line 332, therefore check this code has not been accidently modified. Also ensure line 9 is correct.
'''
from networkx import NetworkXNoPath
'''

### Tool not responding

When processing long routes the tool may display *Not Responding* in the toolbar. This is often the case in Windows, where the operating system assumes that the tool is not responding while the script is running and generating routes. This message can be ignored, routes will generate at the end. This is a commonly reported issue of PyQt. To reduce this issue, close other applications and processes if not required.

## References

Alattar, M. A., Cottrill, C. and Beecroft, M. (2021) Modelling cyclists’ route choice using Strava and OSMnx: A case study of the City of Glasgow. Transportation Research Interdisciplinary Perspectives, 9: 100301. doi:10.1016/j.trip.2021.100301.

Boeing, G. (2017) OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. Computers, Environment and Urban Systems, 65: 126–139. doi:10.1016/j.compenvurbsys.2017.05.004.

Boeing, G. (2020) A multi-scale analysis of 27,000 urban street networks: Every US city, town, urbanized area, and Zillow neighborhood. Environment and Planning B: Urban Analytics and City Science, 47 (4): 590–608. doi:10.1177/2399808318784595.

Clemens, K. (2015) Geocoding with OpenStreetMap Data. GEOProcessing : The Seventh International Conference on Advanced Geographic Information Systems, Applications, and Services. Available at: https://personales.upv.es/thinkmind/dl/conferences/geoprocessing/geoprocessing_2015/geoprocessing_2015_1_10_30013.pdf [Accessed: 30 April 2024].

Earth Data Science (n.d.) Interactive Maps in Python | Earth Data Science - Earth Lab. Available at: https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-spatial-data/customize-raster-plots/interactive-maps/ [Accessed: 30 April 2024].

London Datastore (n.d.) London Atmospheric Emissions Inventory (LAEI) 2019 - London Datastore. Available at: https://data.london.gov.uk/dataset/london-atmospheric-emissions-inventory--laei--2019 [Accessed: 30 April 2024].

OpenWeatherMap (n.d.) Air Pollution - OpenWeatherMap. Available at: https://openweathermap.org/api/air-pollution [Accessed: 30 April 2024].

Serere, H.N., Resch, B. and Havas, C.R. (2023) Enhanced geocoding precision for location inference of tweet text using spaCy, Nominatim and Google Maps. A comparative analysis of the influence of data selection. PLOS ONE, 18 (3): e0282942. doi:10.1371/journal.pone.0282942.



