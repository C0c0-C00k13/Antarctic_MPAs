import os
os.system("conda install -c conda-forge earthaccess")

import earthaccess

os.environ["EARTHDATA_USERNAME"] = ""
os.environ["EARTHDATA_PASSWORD"] = ""

earthaccess.login(strategy="environment")

results = earthaccess.search_data(
    short_name="MODIS_AQUA_L3_SST_THERMAL_MONTHLY_9KM_DAYTIME_V2019.0",
    temporal=("2002-12-01", "2002-12-31"),
)

earthaccess.download(results, "./data/2002")

# Loop on summers from 2003 to 2010
for year in range(2003, 2011):
    results = earthaccess.search_data(
        short_name="MODIS_AQUA_L3_SST_THERMAL_MONTHLY_9KM_DAYTIME_V2019.0",
        temporal=(f"{year}-01", f"{year}-04"),
    )
    
    earthaccess.download(results, f"./data/{year}")
    
    results = earthaccess.search_data(
        short_name="MODIS_AQUA_L3_SST_THERMAL_MONTHLY_9KM_DAYTIME_V2019.0",
        temporal=(f"{year}-12", f"{year}-12"),
    )

    earthaccess.download(results, f"./data/{year}")

if len(os.listdir('data'))>0:
    print(f"Download complete\n{os.listdir('data')}")
else:
    print("Directory is empty")