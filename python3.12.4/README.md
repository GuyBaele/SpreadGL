
## Data processing tools installation instructions with Python v3.12.4 using `conda` or `mamba`

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
