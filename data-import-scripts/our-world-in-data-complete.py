from shared import create_or_update_dataset
import requests
import pandas
import os
import tempfile
import datetime
from edelweiss_data import QueryExpression as Q

name = "COVID-19 complete dataset by Our World In Data"
url = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"


def get_metadata(now, regions):
    today = datetime.datetime.now()
    # Our world in data mainly uses data that is reported and compiled until 10 CEST -> 8 UTC but there is some delay until publishing
    reporting_day = today if today.hour >= 18 else today - datetime.timedelta(days=1)
    estimated_reporting_cutoff = datetime.datetime(
        reporting_day.year,
        reporting_day.month,
        reporting_day.day,
        8,
        tzinfo=datetime.timezone.utc,
    )
    return {
        "datetimeRetrieved": "{}".format(now),
        "upstreamSource": url,
        "originalDataCollectionAgency": "https://www.ecdc.europa.eu/en/coronavirus",
        "dataBackgroundInformation": "https://ourworldindata.org/coronavirus-source-data",
        "estimatedReportingCutoff": "{}".format(estimated_reporting_cutoff),
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "by country", "testing"],
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "columnNames": {
            "region": "location",
            "date": "date",
            "daily-cases": "new_cases",
            "total-cases": "total_cases",
            "daily-deaths": "new_deaths",
            "total-deaths": "total_deaths",
            "population": "population",
        },
        "regions": regions,
    }


def get_description(now):
    return """# COVID-19 data for all countries
### Compiled and aggregated by the European Centre for Disease Prevention and Control via Our World In Data

This dataset was created at {} created once daily around 6pm CET from [the original dataset by our world in data]({}) which in turn sources the data from the European Centre for Disease Prevention and Control (ECDC)
([more information on the process](https://ourworldindata.org/coronavirus-source-data)).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/")
        """.format(
        now, url
    )


def get_data():
    dataframe = pandas.read_csv(url)
    return dataframe


now = datetime.datetime.now(datetime.timezone.utc)
description = get_description(now)
data = get_data()
metadata = get_metadata(now, [ l for l in data.loc[:,"location"].unique() ])
create_or_update_dataset(name, url, metadata, description, data)
