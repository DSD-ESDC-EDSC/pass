# Database Initialization

To set up the database for PASS, you will need to run `db_init.py`. For this Python script to successfully run, the following steps need to be complete prior.

1. Start up API for calculating distance matrix. For this tool, the OpenRouteService at the minimum must be running. Refer to the documentation within the [pass_distance_matrix_api markdown](/pass_distance_matrix_api.md) for more information on setting this up.
2. Set up a `modules/config.json`. Refer to the section below on how to prepare this file for successful read.

## config.json

The `config.json` file is meant to describe your data sources for `db_init.py` to read, prepare and store the data sources into the PostgreSQL database. The `config_template.json` file can be used to build a version of `config.json`. This section explains the necessary and optional objects that need to be present in the JSON.

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


```
