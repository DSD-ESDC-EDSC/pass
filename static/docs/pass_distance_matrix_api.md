# Distance Matrix Calculation Set Up Instructions

The following document provides detailed instructions for how to set up the APIs to calculate distance matrixes for both car and public transit. In order for `db_init.py` to initialize the distance_matrix database table, `DistanceMatrix()`, the following API needs to be installed: 

1. Open Route Service API for cars

The Open Trip Planner API for public transit is currently being developed and thus is not needed to run DistanceMatrix(). If you are interested in supporting the creation of this read the section below and follow contribution steps provided in the [README.md](../README.md).

Both APIs are java based, the Open Route Service (ORS) API is initialized using Docker for the car distance calculations, while a Java file (.jar) runs a virtual machine for Open Trip Planner's API to calculate distances based on General Transit Feed Specification (GTFS) public transit data. 

Both APIs depend on OpenStreetMap road network data, a reliable data source for road data in Canada (Zhang 2018; Jacobs 2017). You can download the OSM data for Canada from Geofabrik's server: [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf). There are instructions below on how to reduce the size of this file. 

Depending on the geographic scope, you might have memory issues, especially for the Open Trip Planner API. It is suggested to select the smallest possible geographic scope to reduce memory issues.

# Car Distance Matrix

## Dependencies
- [Docker](https://docs.docker.com/)
- [Open Route Services (ORS) repo](https://github.com/GIScience/openrouteservice). Learn more about ORS via their [documentation](https://github.com/GIScience/openrouteservice-docs) and their [website](https://openrouteservice.org/)

## Data Source
- Download Geofabrik's latest OSM data for Canada: [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf)

## Installation
There are different steps to install ORS depending on the Operating System. As such, refer to the Installation steps in ORS GitHub repo's [README.md](https://github.com/GIScience/openrouteservice/blob/master/README.md).

## Run
Once you follow the ORS's steps to install, the API must be turned on in order for DistanceMatrix() class to work. If using Docker, simply run the following commands: `docker-compose up`.

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
