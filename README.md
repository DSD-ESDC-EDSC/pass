# POI Potential Spatial Accessibility Web App

This repository of code provides scripts for calculating potential spatial accessibility from population demand locations (e.g., Dissemination Area population-weighted centroids) to points of interest (POS). Accessibility, that is the ability to get from location A to B, is a multi-dimensional construct that can account for various components, like social and geographic. Moreover, access can be measured based on `potential` (i.e., based on who could access a given service) and/or `actual` demand (i.e., based on a given services' actual clients/users of the service). **Potential spatial accessibility looks at the availability (i.e., supply and capacity of services) and accessibility (i.e., barriers) of potential demand (e.g., Census demographics) to a given service.**

# Installation

### Dependencies

- Anaconda > 4.0 (National Service Desk)
- Git Bash (Application Catalogue)
- PostgreSQL > 11
- PostGIS (PostgreSQL extension) > 2.5

### Steps to Install

1. Make sure you have the above dependencies installed
2. To make Anaconda run from Git Bash, you will have to change your Environment Variables on your user account:
	- Open the application "Edit environment variables for your account"
	- Add a new variable PATH if it doesn't exist, otherwise add the following to the PATH variable: `C:\ProgramData\Anaconda3; C:\ProgramData\Anaconda3\Scripts`
3. Now in Git Bash, clone the repo: `git clone https://gccode.ssc-spc.gc.ca/DSCV/projects/pos-accessibility/pass`
4. Still in Git Bash, change directory to the folder: `cd pass`
5. Then in Git Bash clone the Anaconda environment from the environment.yml file: `conda env create -f environment.yml`
6. Once you have all the dependencies installed, activate the environment: `source activate pass`
7. You will also need to create a `.env` file within the same directory. The following information should exist within the file, but with add values specific for your use case:

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

# Run

Once you completed the Installation step, which you only need to complete once, to run the actual web app from now on, you must complete the following:

1. Open Git Bash and change directory (cd) to your `app` folder. Alternatively, in your windows explorer (1) go to the app folder and (2) right-click and select 'Git Bash Here', and then Git Bash will open within your app folder
2. Now with Git Bash opened within your app folder, activate your Anaconda environment: `source activate pass`
3. Run the following command in Git Bash to start the app: `python app.py`
4. After running the command, go to your browser, and you can open the app with your provided `APP_HOST:APP_PORT`
5. To close the app, in Git Bash press the Ctrl + C keys

# Contribute

- Assign yourself to an issue
- Create new branch related to that issue
- Pull from master branch (this might get updated eventually to dev once a first version is stable)
- Work on your branch, when you have completed the code and tested it, you can then push the branch to the remote repository
- Make a merge request in GCCode, @Noznoc will review and merge into master
