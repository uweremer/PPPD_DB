# PPPD

The purpose of **PPPD** (**P**rojekt-**P**olizei-**P**resse-**D**aten) is mainly to scrape press releases from [Presseportal-Blaulicht](https://www.presseportal.de/blaulicht/) and extract the relevant data to use it in research projects.


## 1. Installation
1. Clone/download this repository.
2. Populate `config.ini` (see [`config.ini[EXAMPLE]`](config.ini[EXAMPLE]), use `DEVEL_MODE=True` to toggle the webscraping to a small subset as proof of concept).
3. Install the dependencies from `requirements.txt`. 



## 2. Usage

The simplest way of scraping press releases from [Presseportal-Blaulicht](https://www.presseportal.de/blaulicht/) is to use the function `get_blaulicht_data()` from the module `ppRunner`. This function downloads and processes every press release from every newsroom in the given federal states and years of interest.

In the following example, the function is used to download all press releases from 2020 (years=2020) posted by police departments (dept_type="police") in Baden-Württemberg (states="baden-württemberg"). A folder named "ppp_bw" (output_folder_name="ppp_bw") will be created within the project folder and all data will be stored in it.

```python
from src import ppRunner as ppr

ppr.get_blaulicht_data(
    states="baden-württemberg",                         
    years=2020,                                         
    dept_type="police",
    output_folder_name="ppp_bw",
)
```


**Multiple states and years at once**

The arguments *states* and *years* can both be either a single value or a list of values. In the following example, multiple federal states and multiple years are specified. Caution: The execution of the code below may take a few days.

```python
from src import ppRunner as ppr

ppr.get_blaulicht_data(
    states=["baden-württemberg", "hessen", "niedersachsen"],                         
    years=[2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],                                         
    dept_type="police",
    output_folder_name="example_project",
)
```


## 3. Database usage

If you want to use PostgreSQL as database, fire up a docker environment e.g. as provided in the `docker-compose.yml`: 

```sh 
sudo docker-compose -f docker-compose.yml --env-file config.ini up -d
```  

Don't forget to provide the credentials within the `config.ini`.

A sql snapshot of the imported legacy data is internally available on the S7-Share `~./Projekte/PPPD/output_data/20230427_pppd.sql`. Otherwise, to import legacy data (from csv and txt files from the initial webscraping from folder `./output_data/ppp_bw/`) run the script [`01-load_basic_data.py`](scripts/init_db/01-load_basic_data.py) from the folder `scripts/init_db`. It expects two CLI arguments: The first specifies, whether the db should be initialized from scratch (`init`: old data will be deleted, `append`: data will be appended), the second argument specifies the year to import.

```sh
# First run to initialize the db and to import 2015 data:
python 01-load_basic_data.py init 2015

# Subsequent runs (data will be appended) for other years, e.g. 2019:
python 01-load_basic_data.py append 2019
```


## 4. Convenience startup for development

If everything is prepared as suggested above in *2. Installation*, use the script [`start.sh`](start.sh) to:
- start docker service 
- stop and clean up all containers 
- clean the (otherwise) persistent database volume
- initialize containers 
- editable (`-e` flag) install of the project 

The script expects the path to the Python environment as CLI argument. And dont forget to make it executable and to begin with a leading`./`.  

```sh
chmod +x start.sh
./start.sh PATH_TO_ENV
```

### Further notes

- Don't forget to select the virtual environment as interpreter. If your are working with the VSCode IDE: <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>p</kbd> and type: "Python: Select Interpreter".


## Geolocation 



For geolocation of the reports, run the script [`02-geolocate_reports.py.py`](scripts/init_db/02-geolocate_reports.py.py).
