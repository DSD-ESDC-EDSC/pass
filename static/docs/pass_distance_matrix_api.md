# Distance Matrix Calculation Set Up Instructions

The following document provides detailed instructions for how to set up the APIs to calculate distance matrixes for both car and public transit. In order for `db_init.py` to initialize the distance_matrix database table, `DistanceMatrix()`, the following API needs to be installed: 

1. Open Route Service API for cars

The Open Trip Planner API for public transit is currently being developed and thus is not needed to run DistanceMatrix(). If you are interested in supporting the creation of this read the section below and follow contribution steps provided in the [README.md](../README.md).

Both APIs are java based, the Open Route Service (ORS) API is initialized using Docker for the car distance calculations, while a Java file (.jar) runs a virtual machine for Open Trip Planner's API to calculate distances based on General Transit Feed Specification (GTFS) public transit data. 

Both APIs depend on OpenStreetMap road network data, a reliable data source for road data in Canada (Zhang 2018; Jacobs 2017). You can download the OSM data for Canada from [Geofabrik's server](https://www.geofabrik.de/data/download.html): [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf). There are instructions below on how to reduce the size of this file. 

Depending on the geographic scope, you might have memory issues, especially for the Open Trip Planner API. It is suggested to select the smallest possible geographic scope to reduce memory issues.

# Car Distance Matrix

## Dependencies
- [Docker](https://docs.docker.com/)
- [Open Route Services (ORS) repo](https://github.com/GIScience/openrouteservice). Learn more about ORS via their [documentation](https://github.com/GIScience/openrouteservice-docs) and their [website](https://openrouteservice.org/).

## Data Source
- Download Geofabrik's latest OSM data for Canada: [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf)

If you are only interested in a specific locality or region, you can select provincial OSM data to download within Geofabrik. Then you can use a tool like `osmosis` to subset the OSM data to a specific bounding box or region. The [learnOSM](https://learnosm.org/en/) tutorial ["Manipulating Data with Osmosis"](https://learnosm.org/en/osm-data/osmosis/) provides information on how to use `osmosis` for processing OSM data.

## Installation
There are different steps to install ORS depending on the Operating System. As such, refer to the Installation steps in ORS GitHub repo's [README.md](https://github.com/GIScience/openrouteservice/blob/master/README.md). For those with a Windows OS, check out the ["Install and run openrouteservice with docker" documentation](https://github.com/GIScience/openrouteservice/blob/master/docker/README.md).

General steps though are the following:

1. Copy/paste `*.osm.pbf` into the `openrouteservice/docker/data` folder.
2. In `openrouteservice/docker/docker-compose.yml` change the `OSM_FILE` variable to the desired OSM data file.
3. Make sure Docker is running, and then enter into, for example, Git Bash the following: `docker-compose build` to build the container.

If you prefer to change certain components of the API, refer to the [ORS documentation](https://github.com/GIScience/openrouteservice-docs).

## Run
Once you follow the ORS's steps to install, the API must be turned on in order for DistanceMatrix() class to work. If using Docker, simply run the following commands: `docker-compose up`. Make sure in the `config.json` your prefered settings are set up (e.g., units). For further information on `config.json` preferences for the API, refer to [pass_config.md](./pass_config.md)

# Public Transit Distance Matrix

THIS IS CURRENTLY IN DEVELOPMENT AND IS NOT AVAILABLE FOR USE. IF YOU ARE INTERESTED IN CONTRIBUTING, PLEASE READ THE SECTION BELOW AND FOLLOW THE CONTRIBUTION STEPS PROVIDED IN THE [README.md](../README.md)

## Dependencies
- [Open Mobility Data API](https://transitfeeds.com/) key to download the GTFS feeds from Canada the TransitFeed: [download key here](https://transitfeeds.com/api/keys). Add this key to your .env file with a new variable: `GTFS_API_KEY`
- OpenTripPlanner (OTP) Java: [download latest shaded.jar file here](https://repo1.maven.org/maven2/org/opentripplanner/otp/). Learn more about installing OTP via [this tutorial](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/)

## Data Source
- Download GTFS feeds using [gtfs.py](/modules/gtfs.py) script
- Download Geofabrik's latest OSM data for Canada, the ways (roads and paths) will be used as well as the GTFS data for calculating commute time: [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf)

## Installation

## Run
