### data processing tools using python3.12.4 on Mac OS Sonoma 14.5 (July 31st, 2024)
1. Download & install [Python v3.12.4](https://www.python.org/downloads/). Download & install the latest version of [Git](https://git-scm.com/downloads) for command-line $
2. Open a terminal on your computer and run the following commands:
`git clone https://github.com/GuyBaele/SpreadGL.git` to clone this repository to your local computer; or browse to [the spread.gl GitHub repository](https://github.com/Gu$
`cd SpreadGL` to enter the cloned 'SpreadGL' directory;
`python3.12 -m venv .venv` to create a Python v3.12 virtual environment called '.venv';
`source .venv/bin/activate` to activate the created virtual environment;
`cd scripts` to change the working directory to the 'scripts' folder containing the relevant scripts;
`pip install --upgrade pip` to update pip itself;
`pip install setuptools` or `pip install --upgrade setuptools` to update to the latest version;
`pip install numpy==1.26.4` to install version 1.26.4 (February 5th, 2024) of NumPy;
`pip install geopandas` to install GeoPandas (https://pypi.org/project/geopandas/);
`pip install pyproj` to install pyproj (https://pyproj4.github.io/pyproj/stable/index.html);
`export PROJ_DIR=/usr/local` to set the  path to the base directory for PROJ;
`brew update` to ensure Homebrew is up to date;
`brew install ant` to install Ant (https://ant.apache.org/), used to build Java applications;
`brew install gdal --HEAD` to install the GDAL (https://gdal.org/) headers files first;
`brew install gdal` to install GDAL;
`cp requirements.txt ../scripts/.` to copy the configuration file for use with python3.12.4 to the scripts directory;
`pip install .` to install our command-line data processing tools.
3. You should now be able to process your own data for visualisation in spread.gl (but see the next sections).
