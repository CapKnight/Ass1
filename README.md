# Renewable Energy Dashboard

A web application that visualizes renewable energy output as a percentage of total electricity output for countries worldwide. It features interactive charts, an interactive world map, and tools for comparing data across countries.

## Features

- **Bar Charts**: Display renewable energy data for filtered countries based on region and income level.
- **Country List**: A paginated list showing countries with details like region, income level, and the latest renewable energy output.
- **Interactive World Map**: A color-coded map displaying renewable energy percentages. Hover over countries to view detailed data.
- **Comparison Tool**: Select multiple countries to dynamically compare their renewable energy data.
- **Line Charts**: View historical renewable energy data for individual countries.
- **Responsive UI**: Flexbox-based layout ensures compatibility across different screen sizes.
- **Basic Error Checking**: Handles unexpected issues and displays errors gracefully.

## Setup Instructions

Follow these steps to set up the project locally:
**(If using my Codio, the environment is pre-configured; simply use these two lines: `source .venv/bin/activate` and `python3 manage.py runserver 0.0.0.0:8000`)**

1. Run `git clone https://github.com/CapKnight/Ass1.git` to clone the code to your device.

2. Activate the virtual environment:
   - Create a virtual environment if it doesn't exist: `python3 -m venv .venv`.
   - Activate it: `source .venv/bin/activate`.

2. Run `pyenv install 3.10.7` to install the required Python version.

4. Run `pip install --upgrade pip`.

6. Install required packages: `pip install -r requirements.txt`.

7. Start the server: `python3 manage.py runserver 0.0.0.0:8000`.

8. Copy this in a new tab to access th websit `https://watchquest-analogbogart-8000.codio-box.uk/`

## Prerequisites

This project requires Python 3.10.7 and the packages specified in `requirements.txt`. Install them using:
```
pip install -r requirements.txt
```

## Test

- run `python3 manage.py test`


## Usage

- **Home Page**: Displays a bar graph and a list of countries. Use the filter options to view data for specific regions or income levels. Click on a country's name to see detailed data.
- **Map Page**: Explore an interactive world map where countries are colored based on their renewable energy output percentage. Hover over a country to view more details. Use the mouse and scroll wheel to zoom and pan.
- **Compare Page**: Select multiple countries to compare their renewable energy data through dynamic visualizations.

## Source

Data is sourced from MyAberdeen.
Map data sourced from [Natural Earth Data](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/).
