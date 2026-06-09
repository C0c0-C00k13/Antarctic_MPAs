# Description
This repository contains scripts processing East Antarctic ecosystem features and returns the likely distinct bioregions through clusterings

# Usage
A virtual environment is needed to run the dependencies.

## Run on Galaxy
If you plan on running the script on Galaxy.eu, you can use Jupyter Notebook Interactive tool.*

\* A Galaxy account is required to use the tool

## Run on local or another 
You can use `environment.yml`to create the proper environment.

# Required packages
* r-r.utils 
* r-tidyverse 
* libgdal-hdf5 
* r-ggplot2
* r-rcpp 
* openssl 
* r-sf 
* r-terra 
* r-ncdf4
* r-lubridate
* r-rcolorbrewer 
* r-lattice 
* r-png
* r-raster
* r-fnn
* r-cluster 
* r-remotes 
* r-devtools

```bash
conda create --file environment.yml
```