# Database Initialization

To set up the database for PASS, you will need to run `db_init.py`. For this Python script to successfully run, the following steps need to be complete prior.

1. Start up API for calculating distance matrix. For this tool, the OpenRouteService at the minimum must be running. Refer to the documentation within the [pass_distance_matrix_api markdown](/pass_distance_matrix_api.md) for more information on setting this up.
2. Set up a `modules/config.json`. Refer to the section below on how to prepare this file for successful read.

## config.json

The `config.json` file is meant to describe your data sources for `db_init.py` to read, prepare and store the data sources into the PostgreSQL database. The `modules/config_template.json` file can be used to build a version of `config.json`. This section explains the necessary and optional objects that need to be present in the JSON.

TO DO: COMPLETE THIS!

The main `file` objects and their key/values that **need** to be in `config.json` are the following:

- `demand_geo`: the ***.shapefile** of the desired geographic unit to measure and visualize spatial accessibility.
  - `file`
  - `type`
  - `crs`
  - `columns`
  
- `demand_pop`: the ***.csv** of `demand_geo` geographic unit's population.
  - `file`
  - `type`
  - `encoding`
  - `crs`
  - `columns` 


- `supply`: the ***.csv** of the desired Points of Interest (POI) (i.e., service) location (latitude and longitude)
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
	}
}

```
