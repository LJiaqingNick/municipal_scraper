# Municipal Scraper

The Canadian Municipal Scraper is a project designed to gather information about Canadian municipal councillors and mayors from various municipal websites. It features a collection of scrapers tailored to the unique structure of each municipality's website, such as `toronto_scraper.py` for the City of Toronto.

## Description

This project is structured to allow for scalability and maintainability. Each municipality's scraper is a separate script within the `scraper` directory, ensuring that modifications to one scraper do not impact the others. Utility functions are centralized in the `utils` directory to promote code reuse and simplify maintenance.

## Setup

To run this project, you will need Python 3.6+ installed on your machine. To set up the project environment:

1. Clone the repository:
    ```sh
    git clone https://github.com/LJiaqingNick/municipal_scraper.git
    cd municipal_scraper
    ```
2. (Optional) Create a virtual environment:
    Use python's built-in venv module to create a virtual environment. This will allow you to install the required packages without affecting your system's python installation. Link to [venv documentation](https://docs.python.org/3/library/venv.html).
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```
    Or using Anaconda. Link to [Anaconda documentation](https://docs.anaconda.com/anaconda/install/)
    ```sh
    conda create --name <env_name> python
    conda activate <env_name>
    ```


2. Install the required packages:
    ```sh
    python -m pip install -r requirements.txt
    ```
3. To make `utils` directory available as a package, run the following command:
    ```sh
    python -m pip install -e .
    ```
## Usage
To run the individual scrapers, use the following command(make sure you are in the municipal_scraper directory):
```sh
python scraper/<scraper_name>_scraper.py
```
To run all the scrapers, use the following command(make sure you are in the municipal_scraper directory):
```sh
python main.py
```
The main.py script will execute each municipal scraper sequentially and gather all data.

## Overview of folder structure

    Your project directory should now look like this:
    municipal_scraper/
    │
    ├── scraper/
    │ ├── init.py
    │ ├── <scraper_name>_scraper.py
    │ └── ...
    │
    ├── utils/
    │ ├── init.py
    │ └── help_functions.py
    │
    ├── main.py
    ├── .gitignore
    ├── setup.py
    ├── README.md
    └── ...
