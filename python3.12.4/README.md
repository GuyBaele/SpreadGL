## data processing tools installation instructions with Python v3.12.4 using `conda` or `mamba`

### Prerequisites

Ensure that you have either **conda** or **mamba** installed on your system. Mamba is recommended for its faster installation speed. 
You can download the latest version of Miniconda with Python v3.12.4 for any OS [here](https://docs.anaconda.com/miniconda/#miniconda-latest-installer-links).

### Instructions

Follow these steps to set up your environment (if you already have `bioconda` and `mamba` installed, skip to step 3:

0. **Make sure bioconda is set up**

   Make sure you hav access to the conda-forge and bioconda channels. To set this up, run the following commands in your terminal:

   ```bash
   conda config --add channels bioconda
   conda config --add channels conda-forge
   conda config --set channel_priority strict

   ```

1. **Install `mamba`**

   Install `mamba` in your base environment if it's not already installed. To do so, run the following command in your terminal:

   ```bash
   conda install mamba
   ```

   After the installation is done, initialize it in your shell with:
   ```bash
   mamba init
   ```
   
2. **Restart Terminal**

   After initializing `mamba`, close your terminal and open a new terminal session to apply the changes.

   Check if `git` is available in your terminal by typing `git --help`. If not, you can install it typing `mamba install git`

3. **Create a new environment for the Spread.gl data processing tools**

   Create a new `mamba` environment called `spreadgl` and activate it

   ```bash
   mamba create -n spreadgl
   mamba activate spreadgl
   ```

4. **Download Spread.gl**

   Clone the Spreag.gl repository with `git`:

   ```bash
   git clone https://github.com/GuyBaele/SpreadGL.git
   ```

4. **Install required dependencies**
   
   Install all required dependencies in the `requirements.txt` file inside the `SpreadGL/pyhon3.12.4` folder.

   ```bash
   mamba install --file requirements.txt
   ```
5. **Install the Spread.gl processing tools**

   Go to the `SpreadGL/scripts` folder and install the tools typing:

   ```bash
   pip install .
   ```

   You have now installed the Spread.gl tools. You can check that you have access to them by typing `spread --help` on the terminal!



## data processing tools using python3.12.4 on Mac OS Sonoma 14.5 (July 31st, 2024)
1. Download & install [Python v3.12.4](https://www.python.org/downloads/). Download & install the latest version of [Git](https://git-scm.com/downloads) for command-line use, or [GitHub Desktop](https://github.com/apps/desktop) if you prefer a graphical user interface to clone our spread.gl repository (see the next step).
2. Open a terminal on your computer and run the following commands:  
`git clone https://github.com/GuyBaele/SpreadGL.git` to clone this repository to your local computer; or browse to [the spread.gl GitHub repository](https://github.com/GuyBaele/SpreadGL), click '<> Code ▼' and select 'Open with GitHub Desktop' if you chose to use GitHub Desktop in the previous step;  
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
