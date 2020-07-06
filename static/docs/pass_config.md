# Database Initialization

To set up the database for PASS, you will need to run `InitSchema` Python class. The `InitSchema.py` file runs several different modules to read, process and store the necessary data for PASS. **For this Python script to successfully run, the following steps must be completed prior**:

1. Set up a `config.json`. Refer to the section below on how to prepare this file for successful read.

2. Connect to either a local or web version of the [OpenRouteService (ORS)](https://github.com/GIScience/openrouteservice) API for calculating a drive time/distance matrix.
  - `InitSchema.py` runs the `DistanceMatrix` class that connects to this API to calculate drive time/distance isochrones and then a distance matrix file to be stored in the database. 
  - `DistanceMatrix` depends on the `client_url` parameter, which can be provided in `config.json`. Either provide a web client URL (in which case you will need to [sign up for ORS web API](https://openrouteservice.org/plans/)) or set up a local version of the API through a virtual machine / container. If you are working with larger geographic extents (e.g., all of Canada), it is recommended to host locally to avoid dealing with API limits. **For information on how to install ORS locally, refer to the [Distance Matrix Calculation Set Up Instructions](/pass_distance_matrix_api.md)**.

3. Assuming [PostgreSQL](https://www.postgresql.org/) is already installed, initialize a new database and add the [PostGIS](https://postgis.net/) database extension to store the geographic data. Make sure to add the PostgreSQL database connection information to `config.json`.

## config.json

The `config.json` file is meant to describe your data sources for `InitSchema.py` to read, prepare and store into the PostgreSQL database (`files` key); moreover, it provides the following: (1) connection information for the database (`DB` key), (2) connection information for the `DistanceMatrix` local/web API (`ORS` key), (3) app configuration variables (`APP` key), and (4) variables for logging (`LOGGER` key). The `config_template.json` file can be used to build a version of `config.json`. This section explains the necessary and optional objects that need to be present in this JSON.

The `files` object and their key/values that **need** to be in `config.json` are the following:

- `demand_geo`: the `*.shapefile` of the desired geographic unit to measure and visualize spatial accessibility.
  - `file`
  - `type`
  - `crs`
  - `columns`
  
- `demand_pop`: the `*.csv` of `demand_geo` geographic unit's population.
  - `file`
  - `type`
  - `encoding`
  - `crs`
  - `columns` 

- `supply`: the `*.csv` of the desired Points of Interest (POI) (i.e., service) location (latitude and longitude)
  - `file`
  - `type`
  - `encoding`
  - `crs`
  - `columns`

There is an *optional* object `demand_geo_weight` that you can also include to create population weighted centroid, that is the centriod is weighted based on populations at a more granular geographic unit.

- `ORS_params`


```
{
	"files": {
		"demand_geo": {
			"file":"C:/Users/Name/Documents/Code/pass/data/demand_geo.shp",
			"type":"shape",
			"crs": "3347",
			"columns": {
				"ID" : {
					"name": "DAUID",
					"type": "geouid",
					"unit": "int",
					"desc": "ID"
						},
				"LRG_ID" : {
					"name": "CMAUID",
					"type": "lrg_id",
					"unit": "int",
					"desc": "ID"
						},
				"geometry": {
					"name": "geometry",
					"type": "geometry",
					"unit": "geometry", 
					"desc": "geometry"
						}
				}
			},
		"demand_pop": {
			"file":"C:/Users/Name/Documents/Code/pass/data/demand_pop.csv",
			"type":"demand",
			"encoding":"latin-1",
			"columns": {
				"ID": {
					"name":"geouid",
					"type":"geouid",
					"unit": "int",
					"desc": "ID"
					},
				"demand_total": {
					"name":"total_pop",
					"type": "pop_Total",
					"unit": "int", 
					"desc": "demand"
					},
				"demand_variable": {
					"name": "total_variable",
					"type": "Variable Population",
					"unit": "int", 
					"desc": "demand"
				  },
			}
		},
    "demand_geo_weight": {
      "file": "C:/Users/Name/Documents/Code/pass/data/demand_geo_weight.shp",
      "type": "shape",
      "crs":"epsg:3347",
      "columns": {
        "ID" : {
          "name": "DBUID",
          "type": "geouid",
          "unit": "int"},
        "LRG_ID" : {
          "name": "DAUID",
          "type": "lrg_id",
          "unit": "int"},
        "geometry": {
          "name": "geometry",
          "type": "geometry",
          "unit": "geometry"
            }
          }
    },
		"supply": {
			"file":"C:/Users/Name/Documents/Code/pass/data/poi.csv",
			"type":"supply",
			"encoding":"latin-1",
			"crs":"4326",
			"columns": {
				"ID": {
					"name":"OBJECTID",
					"type":"geouid",
					"unit": "int", 
					"desc": "ID"
					},
				"latitude" : {
					"name":"Latitude",
					"type":"latitude",
					"unit": "float", 
					"desc": "geometry"
				},
				"longitude" : {
					"name":"Longitude",
					"type":"longitude",
					"unit": "float", 
					"desc": "geometry"
				},
				"LRG_ID" : {
					"name":"CSDUID",
					"type":"lrg_id",
					"unit": "str", 
					"desc": "ID"
				}
				"name": {
					"name":"Site_Name",
					"type": "Name",
					"unit": "text", 
					"desc": "info"
				},
				"type": {
					"name":"Site_Type",
					"type": "Type",
					"unit": "text", 
					"desc": "info"
				},
				"supply_services": {
					"name": "services",
					"type": "Number of Services Offered",
					"unit": "int", 
					"desc": "supply"
				},
				"capcity_size": {
					"name":"size",
					"type": "Size (squared meters) of POI service",
					"unit": "int", 
					"desc": "capacity"
				}
			}
		}
	},
	"ORS_params": {
		"connection": {
			"client_url": "http://HOST:PORT/ors",
			"timeout": 500
		},
		"isochrones": {
			"catchment_range": 3600,
			"catchment_range_type": "time",
			"profile": "driving-car",
			"sleep_time": 0
		},
		"distance_matrix": {
			"metric": "distance",
			"unit": "m" ,
			"sleep_time": 0
		}
	},
	"DB": {
		"HOST": "DB HOST",
		"PORT": "DB PORT",
		"NAME": "DB NAME",
		"PASSWORD": "DB PASSWORD",
		"USER": "DB USER"
	},
	"APP": {
		"SECRET_KEY": "pass",
		"HOST": "HOST",
		"PORT": "PORT",
		"THREADS": 4
	},
	"LOGGER": {
		"DEFAULT_LEVEL": "debug",
    "FILE": "False"
		"FILE_PATH": "C:/Users/Name/Documents/Code/pass/pass.log"
	}
}

```
