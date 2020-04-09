# Potential Spatial Accessibility Software Service (PASS)

This repository of code provides scripts for calculating potential spatial accessibility from population demand locations (e.g., Dissemination Area population-weighted centroids) to points of interest (POI). To learn more about the methodology used, checkout docs/pass_doc.html.

# Installation

### Dependencies

- Python > 3.6
- PostgreSQL > 11
- PostGIS (PostgreSQL extension) > 2.5
- Docker
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
