# Distance Matrix Calculation Set Up Instructions

The following document provides detailed instructions for how to set up an application programming interface (API) to calculate distance matrixes for car. **It is highly recommended to read the [PASS report that details the methodology to measure spatial accessibility](./pass_report_20200422.html), specifically the 'Floating Catchment Area (FCA) Methods: 2SFCA and Enhanced 3SFCA Models' and 'Data' sections, to better understand why a distance matrix is necessary for PASS to operate**.

Currently PASS only depends and can use a distance matrix calculated by cars as a mode of transportation. Thus, in order for `InitSchema.py` to create the `distance_matrix_car` database table, through the use of the `DistanceMatrix` class, the following [OpenRouteService (ORS)](https://github.com/GIScience/openrouteservice) API connection needs to be established and then provided within `config.json`. (There is also documentation below on how we are trying to incorporate public transit as a mode of transportation for PASS through the use of the [OpenTripPlanner (OTP)](https://docs.opentripplanner.org/en/latest/) API.)

The ORS API can be initialized using Docker for the car travel time calculations or [you can create an account on the ORS website](https://openrouteservice.org/plans/) to use their web API. If you want PASS to run for a large geographic extent and/or on a large dataset of POIs, then you will need to setup a containerized version of ORS, which is further explained under the 'Car Distance Matrix' section below.

Both ORS and the OTP APIs depend on [OpenStreetMap (OSM)](https://www.openstreetmap.org) road network data, a reliable data source for road data in Canada ([Zhang 2017](https://ir.lib.uwo.ca/cgi/viewcontent.cgi?article=1364&context=geographypub); [Jacobs 2017](https://kentjacobs.net/assets/thesis.pdf)). You can download the OSM data for Canada from [Geofabrik's server](https://www.geofabrik.de/data/download.html): [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf). There are instructions under 'Data Source' on how to reduce the size of this file. 

**Depending on the geographic scope and your computer specs, you might have memory issues. It is suggested to select the smallest possible geographic scope to reduce memory issues.**

# Car Distance Matrix with OpenRouteService (ORS)

This section details on how to set up a local ORS API instance with Docker. If you are working within a small geographic extent (e.g., a single city) and/or small dataset of POIs (i.e., service locations), then the ORS web API can be used. Details on using their web API can be accessed on the [ORS website](https://openrouteservice.org/plans/), just make sure to include the `client_url` under `ORS` within configuration file, `config.json`.

## Dependencies
- [Docker](https://docs.docker.com/)
- [Open Route Services (ORS) repo](https://github.com/GIScience/openrouteservice). Learn more about ORS via their [documentation](https://github.com/GIScience/openrouteservice-docs) and their [website](https://openrouteservice.org/).

## Data Source
Download Geofabrik's latest OSM data for Canada: [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf)

If you are only interested in a specific locality or region, you can select provincial OSM data to download within Geofabrik. Then you can use a tool like `osmosis` to subset the OSM data to a specific bounding box or region. The [learnOSM](https://learnosm.org/en/) tutorial ["Manipulating Data with Osmosis"](https://learnosm.org/en/osm-data/osmosis/) provides information on how to use `osmosis` for processing OSM data.

There is also the option to identify additional data and convert it into the `osm.pbf` format. Before pursuing this approach though it should be assured that there is no duplicate data if reading in both your own data and OSM data.

## Installation
There are different steps to install ORS depending on the OS. As such, refer to the 'Installation' steps in ORS GitHub repo's [README.md](https://github.com/GIScience/openrouteservice/blob/master/README.md). For those with a Windows OS, check out the ["Install and run openrouteservice with docker" documentation](https://github.com/GIScience/openrouteservice/blob/master/docker/README.md).

General steps though are the following:

1. Copy/paste `*.osm.pbf` into the `openrouteservice/docker/data` folder.
2. The following changes need to be complete in `openrouteservice/docker/docker-compose.yml`:
  - Change the `OSM_FILE` variable to the desired OSM data file. 
  - Update the data file path `./data/*.osm.pbf:/ors-core/data/osm_file.pbf`
  - Change the `BUILD_GRAPHS` environment variable to `TRUE`
  - If you are working with a large OSM data file (greater then 1GB), it is recommended to increase the `-Xms1g` and `-Xmx2g` options within the `JAVA_OPTS` environment variable. You will likely need to update the Docker specs as well.
3. Make sure Docker is running, and then enter into, for example, Git Bash the following: `docker-compose build --no-cache` to build the container with your specific data files.

If you prefer to change certain components of the API, refer to the [ORS documentation](https://github.com/GIScience/openrouteservice-docs).

## Run
Once you follow the ORS's steps to install, the API must be turned on in order for the `DistanceMatrix` class to run successfully. If using Docker, simply run the following commands: `docker-compose up`. If you are working with a large OSM file (greater then 1GB) the container might take some time to boot up. To check the status, enter `[HOST]:[PORT]/ors/health` in your browser. When the `status` value is `ready` then your local API is good to go. Make sure in the `config.json` your preferred settings are set up (e.g., units) under `ORS`. For further information on `config.json` preferences for the API, refer to [pass_config.md](./pass_config.md); though main thing to change in `config.json` is the `client_url` under `ORS`.

# Public Transit Distance Matrix with OpenTripPlanner (OTP)

THIS IS CURRENTLY IN DEVELOPMENT AND IS NOT AVAILABLE FOR USE. IF YOU ARE INTERESTED IN CONTRIBUTING, PLEASE READ THE SECTION BELOW AND FOLLOW THE STEPS IN THE 'CONTRIBUTE' SECTION PROVIDED IN THE [README.md](../README.md).

The aim is to include additional types of modes of transportation into PASS eventually (i.e., additional database tables such as `distance_matrix_transit`), though currently focusing on including public transportation within municipalities that store their data in the General Transit Feed Specification (GTFS). The OpenTripPlanner API for public transit is currently being tested. The plan for calculating a public transit distance matrix is by running a virtual machine for Open Trip Planner's API to calculate distances based on GTFS public transit data, unfortunately there seems to be some limitations with data sizes. If you are interested in supporting the creation of this, please read the 'Public Transit Distance Matrix' section below and follow the steps provided under the `Contribute` section in the [README.md](../README.md).

## Dependencies
- [Open Mobility Data API](https://transitfeeds.com/) key to download the GTFS feeds from Canada the TransitFeed: [download key here](https://transitfeeds.com/api/keys). Add this key to your .env file with a new variable: `GTFS_API_KEY`
- OpenTripPlanner (OTP) Java: [download latest shaded.jar file here](https://repo1.maven.org/maven2/org/opentripplanner/otp/). Learn more about installing OTP via [this tutorial](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/)

## Data Source
- Download GTFS feeds using [gtfs.py](/modules/gtfs.py) script
- Download Geofabrik's latest OSM data for Canada, the ways (roads and paths) will be used as well as the GTFS data for calculating commute time: [canada-latest.osm.pbf](https://download.geofabrik.de/north-america/canada-latest.osm.pbf)

## Installation

TO COMPLETE. IF YOU ARE INTERESTED IN CONTRIBUTING, PLEASE READ THE SECTION BELOW AND FOLLOW THE STEPS IN THE 'CONTRIBUTE' SECTION PROVIDED IN THE [README.md](../README.md).

## Run

TO COMPLETE. IF YOU ARE INTERESTED IN CONTRIBUTING, PLEASE READ THE SECTION BELOW AND FOLLOW THE STEPS IN THE 'CONTRIBUTE' SECTION PROVIDED IN THE [README.md](../README.md).
