![Logo](/guide_images/logo.png)

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

2. Click 'create fork'

![Forking the repo](/guide_images/forkingtherepo.PNG)
**Figure 1 - Forking the repository on GitHub.com**

### Cloning the repository
This can be done via the command line or through GitHub Desktop (or whichever git interface you prefer). 

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
2. Activate the environment, the name will be airpollutionenvironment or similar unless you have changed it.
```
conda activate airpollutionenvironment
```
3. Verify this has been successful by listing the loaded packages
```
conda env list
```

**Anaconda Navigator**
1. Open Anaconda Navigator and go to the Environments tab
2. Select Import, choose .yml file from your machine, and select import (**Figure 3**)
3. Set the environment python file as your IDE interpreter. This can be done by launching IDE from Anaconda Navigator Home, or manually: instructions can be found [here](https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html) for PyCharm and [here](https://code.visualstudio.com/docs/python/environments) for VSE. Usually, this is found at the file path: User/your_Anaconda_location/envs/enviro_name/bin/python

![Importing environment](/guide_images/anaconda.PNG)
**Figure 3 - Importing the environment on Anaconda Navigator**

If conda is not your preferred method of installation, all packages are also available using *pip* and are detailed below.

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

There are two scripts within the repository. The raster.py script is only required if wishing to modify the rasters used. The routeplanner.py script is the main script which runs to produce the tool. It integrates the raster.py script without needing to access it directly.

> [!NOTE]
> The following script breakdown assumes you have set up the git repository and have opened the routeplanner.py script in your preferred integrated development environment (IDE) such as [PyCharm](https://www.jetbrains.com/pycharm/) or [Visual Studio Code](https://visualstudio.microsoft.com/vs/community/). If errors occur on opening the file, please see [Troubleshooting](#troubleshooting).

### 1.0 Importing packages, modules and scripts

Firstly, the relevant packages are imported. OSMnx was chosen as the network analyst package due to its excellent results in numerous studies (Boeing 2017; 2018; Alattar et al. 2021). The package is based off the NetworkX package and builds street networks using OpenStreetMap. This allows for street networks adequate for complex route planning to be created. Geopandas is required to store graph nodes and edges and allows for easy data manipulation.
Gathering user inputs and interpreting these into geographical locations, such that the user does not have to enter in a specific format, is performed using the Nominatim tool within the GeoPy package. This tool has been used in other studies and provides adequate locational accuracy (Serene et al. 2023; Clemens 2015). Although, the tool will often choose the first item that matches the input rather than the most relevant, requiring more specific input. E.g. Camden, New Jersey is returned until Camden, London is specified.

To provide pollution data, an API was preferable, however no API with sufficient resolution high enough for street-by-street measurement was available free-to-use. Free APIs such as OpenWeatherMap (2024) have 11km resolution and are unsuitable for shorter routes. Therefore, rasters are used to provide the air pollution data. This requires high confidence in the raster, hence, a reliable data source is required. Many UK raster maps use interpolation to such a high level that they are unsuitable. London Datastore, a site provided by the Mayor of London's Office, provides a raster of projected pollution for 2025, which uses data from live sensors all over the city. These can be obtained from the Detailed Road Transport section of the London Atmospheric Emissions Inventory (2019), located [here](https://data.london.gov.uk/dataset/london-atmospheric-emissions-inventory--laei--2019). Data for other years, past and present is also available which could be easily implemented into the raster script (more thoroughly discussed in Section 4.3). Rasterio is used to sample these raster maps based on the latitude and longitude of OSMnx nodes to return pollution values along routes. The downside is the tool, in its unmodified state can only be used for the areas it is provided rasters for, currently Greater London.

Finally, it was deemed important for the user to have access to the tool in a way that required no coding knowledge - to the extent of simply pressing run. This allows anyone to be able to follow the above steps and access the tool. An executable file to accompany the script would have been preferable to bypass installation and code altogether. However, due to a bug with PyInstaller when used with Rasterio, this is currently difficult without modification of the package - which would have to happen at the user end to avoid a large amount of additional repositorial code. Py2Exe was also deemed excessive as the user would be required to have Microsoft Visual C Runtime DLL, which could not be guaranteed. The final solution is simply to run the script in any IDE and generate a PyQt Graphical User Interface (GUI). PyQt is chosen due to its inclusion in conda without additional channels. The main alternative, TKinter is also more deprecated in terms of modern UI.

Interactive maps displayed in PyQt are generated using Folium. The need to zoom and analyse routes makes packages such as Cartopy unsuitable. Folium was chosen over popular alternative mapboxjs. Although both are based off JavaScript library leafletjs, Folium's ability to function without an authentication token makes it preferable (Earth Data Science 2024).

### 2.0 Setting up PyQt UI class and building widgets

For the code to be executed within a GUI a PyQt window class must first be set up to house other code. The structure of this is illustrated in **Figure 4**.

![PyQt Layout](/guide_images/layout.PNG)
**Figure 4 - PyQt Structure**

PyQt operates using slots and signals, demonstrated in **Figure 5**. The button widget can have a signal attached to it, which when toggled such as with the click signal of the button, triggers the event of the built-in 'slot' of the button.

![Slots and Signals](/guide_images/signalsandslots.PNG)
**Figure 5 - PyQt Slots and Symbols Structure**

The remaining code in this section establishes a series of widgets using QLabel, QInput, QRadioButton, QProgressBar and QWebEngineView. More information about these widgets can be found [here](https://doc.qt.io/qtforpython-6/overviews/gallery.html). The most important widget is the Find Route button. When clicked, this triggers the main route finding script which underpins the tool (**Section 4.0**).

### 3.0 Setting up PyQt UI layout

Following the PyQt structure (**Figure 4**), a layout is required to house the widgets. Horizontal 'rows' housing multiple widgets are created within a vertical box, alongside standalone widgets such as the QWebEngineView. Inline styling is applied throughout. Radio buttons are used to switch user transport mode. The final initial layout of the GUI is shown in **Figure 6**.

![PyQt GUI](/guide_images/initialui.PNG)
**Figure 6 - PyQt Initial GUI**

### 4.0 Running low-pollution route finder script

The main route-finding script has to be executed as one so as to be easily callable from the PyQt button widget. For ease, it has been further broken up into 4.1, 4.2 etc., shown throughout the code. It is also worth noting that the code is fully annotated with comments and docstrings throughout to assist understanding without having to refer back to this documentation.

#### 4.1 Getting user inputs and geocoding locations

Start and end locations from the PyQt inputs are stored in an Inputs class, which takes in an initial and target location. A class method can then be used to geolocate both locations using the Nominatim tool. A try/except block catches the Attribute error if the Nomantim fails and the user is served a warning (**Figure 7**).

![Error Location](/guide_images/errorlocation.PNG)
**Figure 7 - Location error in GUI**

Due to the raster restrictions the locations must also be checked against the raster boundary, using a function which follows the Inputs class. If the returned Boolean is false this also returns a warning (**Figure 8**).

![Error Boundary](/guide_images/errorboundary.PNG)
**Figure 8 - Boundary error in GUI**

#### 4.2 Processing initial fastest route

The progress bar is first triggered at the start of this section to provide the user with updates on their request. This is done manually with numbers taken as a parameter of the QProgressBar widget, e.g. 20(%). 

A new Locations class is constructed to house data in the correct format for route handling. The class functions are designed to create a geopandas data frame for use in OSMnx graph construction, and get nodes for use in routing. OSMnx creates network 'graphs' consisting of nodes and edges. To ensure a large enough graph is created a buffer box is created. Without this, longer routes are at risk of being cut off and therefore unidentifiable. A buffer of 0.01 was chosen - tested to provide a sufficient balance between speed of processing and size of graph. A sample graph is shown in **Figure 9**.

![Sample Graph](/guide_images/samplegraph.PNG)
**Figure 9 - Graph created using OSMnx showing nodes and edges**

A route is constructed between user nodes. Where this is not possible and a NetworkXNoPath error is produced, this is caught and an error returned, rather than crashing the GUI. Distance calculation is also displayed in the GUI - producing a value in kilometres for the route by converting the route to a geodataframe, summing its edges and rounding the value.

#### 4.3 Finding lower pollution route

The method for making a lower pollution route is shown in the flowchart below (**Figure 10**). 

![Flowchart](/guide_images/flowchart.PNG)
**Figure 10 - Lower pollution route finder flowchart**

Pollutant limits are defined within a function so that the values can be adjusted for different objectives. Limits are defined for PM2.5, PM10 and NO2, the most prevalent and harmful pollutants in London.

> [!NOTE]
> The raster.py script is located within the repository. To change rasters, they should be added to the data folder and the obtainvalue() function modified. If pollutants are changed then the limitervalues() function should be modified also.

A tolerance value is initially set to 1, so it does not modify the limits. All route nodes are checked against the raster, and where they exceed the limit set for that pollutant they are removed from the graph. The route is then redrawn if possible. Where this is not possible, all nodes are put back and the tolerance is increased by 50%. This value was chosen to provide a good balance between speed of processing and providing realistic lower pollution routes. The process then repeats until a new route is found. The user is informed if initial pollution values are low and routes are the same. Six functions form the flowchart process:

- getlocation() - Locates the nodes x and y coordinates
- getgeodata() - Gets pollution data for nodes
- compare() - Compares node pollution data to limits
- goodnode() - Returns true if limits are not exceeded
- processpath() - Checks if all route nodes are 'good nodes'
- restrictedpath() - Route construction function with allowed nodes

Route distance is also collected from the route in the same method as [Section 4.2](#42-processing-inital-fastest-route).

#### 4.4 Styling routes based on pollution

In this section routes are styled and exported to a folium map. An index (below) of pollution values is added to each route edge.

*Edge Pollution Index = (NO2 + PM2.5 + PM10) / Number of values*

This edge pollution index is then used to colour each edge in the folium map. The folium map is constructed with an initial zoom and position based on route length and location - ensuring the route is always central and comprehensively displayed on the screen. CartoDB Positron is chosen as the basemap due to its neutral colours, making the routes more easily visible. Finally, markers are added and the folium map is temporarily saved and drawn in the viewer widget.

### 5.0 Running the application

The application is launched by running the routeplanner.py script. A QApplication instance is created and a window should now launch.

> [!IMPORTANT]
> If the application does not launch, please follow troubleshooting steps in [Troubleshooting](#troubleshooting).

## Example Usage

The tool is capable of inputs such as landmarks, train stations, place names, or postcodes. Some examples are demonstrated below. Routes and points can be hovered over to see details.

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

This is another example with similar distance, but many high pollution junctions and main roads avoided.

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

### Errors in the IDE open opening the file
Errors may be flagged in the IDE on opening the file, such as the IDE not recognising PyQt widgets in the import statements or expecting additional arguments where they are referenced. This is due to version differences, but this does not impact the running of the tool. PyCharm is more likely to produce these errors due to an issue with its communication with conda - VSE has not been found to have these issues. Nevertheless, both run the tool.

### Tool launches but with error messages in the console
On its first use, the tool will create cache folders in the local repository. On first launch, as these cache folders are not present, error messages related to this may exist in the console. These can be safely ignored. On the second launch, this issue should be resolved.

### One or more locations could not be located error message

The Nominatim tool has failed to find a location which matches one of the user inputs. Check spelling and if certain location is spelt correctly, try adding ', London' afterwards. This eliminates global locations being used.

### One or more locations is outside of Greater London Boundary error message

Check that the location is definitely within the Greater London boundary (roughly the M25). If certain the location is within this boundary, try adding ', London' afterwards. This ensures the correct location is used. If this fails, try using postcodes, these are highly likely to be recognised.

### Unable to draw route between locations error message

Due to the tools reliance on OpenStreetMap, occasionally locations cannot be accurately located, resulting in this error. For example, locations near bridges and water may not be recognised as reachable. Where this occurs, attempt using a nearby landmark or postcode to the location required.

### Tool crashes and ModuleError in console

Ensure that airpollutionenvironment.yml is loaded correctly by following the steps in [Setting up the environment section](#setting-up-the-environment). Check that the lines of code in [Section 1.0 Importing packages and modules](#10-importing-packages-modules-and-scripts) are correct and have not been accidently modified. 

### Tool crashes and AttributeError in console

This is usually caused by errors in the Nominatim tool. These should be caught in line 332, therefore check this code has not been accidently modified. Also ensure line 9 is correct:
'''
from networkx import NetworkXNoPath
'''

### Tool not responding

When processing long routes, the tool may display *Not Responding* in the toolbar. This is often the case in Windows, where the operating system assumes that the tool is not responding while the script is running and generating routes. This message can be ignored, routes will generate at the end. This is a commonly reported issue of PyQt. To reduce this issue, close other applications and processes if not required.

## References

Alattar, M. A., Cottrill, C. and Beecroft, M. (2021) Modelling cyclists’ route choice using Strava and OSMnx: A case study of the City of Glasgow. Transportation Research Interdisciplinary Perspectives, 9: 100301. doi:10.1016/j.trip.2021.100301.

Boeing, G. (2017) OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. Computers, Environment and Urban Systems, 65: 126–139. doi:10.1016/j.compenvurbsys.2017.05.004.

Boeing, G. (2020) A multi-scale analysis of 27,000 urban street networks: Every US city, town, urbanized area, and Zillow neighborhood. Environment and Planning B: Urban Analytics and City Science, 47 (4): 590–608. doi:10.1177/2399808318784595.

Clemens, K. (2015) Geocoding with OpenStreetMap Data. GEOProcessing : The Seventh International Conference on Advanced Geographic Information Systems, Applications, and Services. Available at: https://personales.upv.es/thinkmind/dl/conferences/geoprocessing/geoprocessing_2015/geoprocessing_2015_1_10_30013.pdf [Accessed: 30 April 2024].

Earth Data Science (n.d.) Interactive Maps in Python | Earth Data Science - Earth Lab. Available at: https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-spatial-data/customize-raster-plots/interactive-maps/ [Accessed: 30 April 2024].

London Datastore (n.d.) London Atmospheric Emissions Inventory (LAEI) 2019 - London Datastore. Available at: https://data.london.gov.uk/dataset/london-atmospheric-emissions-inventory--laei--2019 [Accessed: 30 April 2024].

OpenWeatherMap (n.d.) Air Pollution - OpenWeatherMap. Available at: https://openweathermap.org/api/air-pollution [Accessed: 30 April 2024].

Serere, H.N., Resch, B. and Havas, C.R. (2023) Enhanced geocoding precision for location inference of tweet text using spaCy, Nominatim and Google Maps. A comparative analysis of the influence of data selection. PLOS ONE, 18 (3): e0282942. doi:10.1371/journal.pone.0282942.



