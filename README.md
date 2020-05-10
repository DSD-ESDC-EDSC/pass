# Potential Spatial Accessibility Software Service (PASS)

The CDO Data Science team developed a geographic information system, Potential Accessibility Software Service (PASS). PASS offers an advanced quantitative approach to measure how spatially accessible population demand is to a given service.

Spatial accessibility is the consideration of how physical and social space and place affect how a population can traverse through it to access a given service. Though abstract in nature, it can be measured through considerations like where potential population demand is located, the geographic distance to get from the population location to the service locations offered, the supply at the service locations, as well as the probability of a population going to one service location over another based on the capacity. PASS uses the enhanced 3-step floating catchment methodology to accomplish this, which is further explained [in this html (best to download and open in browser)](static/docs/pass_report_20200422.html).

PASS lets you select a geographic area of interest by panning and zooming on the interactive map, and lets you define the parameters to model spatial accessibility to better reflect Canada's diverse society. For example, individuals living in urban areas versus rural areas, have different assumptions and considerations for how to access a service.

# Installation

### Dependencies

- Python > 3.6
- PostgreSQL > 11
- PostGIS (PostgreSQL extension) > 2.5
- Docker
- Java Run Time
- Git Bash (optional)
- Anaconda > 4.0 (optional)

### Steps to Install

1. Make sure you have the above dependencies installed
2. Clone repo
3. Set up Python environment, such as with Anaconda: `conda env create -f environment.yml`
4. Once you have all the dependencies installed, activate the environment, such as: `source activate pass`
5. You will also need to create a `.env` file within the local repo's root directory. The following information should exist within the file, but add values specific for your use case:

```
APP_SECRET_KEY=
APP_HOST=
APP_PORT=

DB_HOST=
DB_PORT=
DB_NAME=
DB_PASSWORD=
DB_USER=

GTFS_API_KEY=

LOG_DEFAULT_LEVEL=debug
LOG_FILE_PATH=
```

6. Create a `data` folder within the local repo's root directory. In that folder you should have the following data:

- Geographic data file representing your demand AP (e.g., shapefile of postal code polygons), AKA 'demand'
- CSV file that at least has the demand geographic data file ids and a variable to represent the population counts
- CSV file that stores your POIs, this file should at least have two columns for longitude and latitude, AKA 'supply'
- Optional: a more granular geographic data file + population for calculating mean-weighted centroids to represent the demand locations more precisely

7. Modify `modules/config.json` so that it reflects your data. Please refer to the wiki to learn more on how to update the config.json ** TO COMPLETE **
8. Refer to the wiki to learn about how set up APIs for calculating distance ... ** TO COMPLETE **
9. Run `modules/db_init.py` to initialize your database, this could take a while depending on how large your data is.


# Run

Once you completed the Installation step, which you only need to complete once, to run the actual web app from now on, you must complete the following:

1. Activate your Python environment, e.g., `source activate pass`
3. Run `app.py`, such as in Git Bash: `python app.py`
4. After running the command, go to your browser, and you can open the app with your provided `APP_HOST:APP_PORT`
5. To close the app, in Git Bash press the Ctrl + C keys

# Contribute

- Assign yourself to an issue, or create an issue
- Create new branch related to that issue
- Pull from master branch (this might get updated eventually to dev once a first version is stable)
- Work on your branch, when you have completed the code and tested it, you can then push the branch to the remote repository
- Make a merge/pull request, @Noznoc will review and merge into master
