import pandas
import datetime

from shared import create_or_update_dataset

name = "COVID-19 complete dataset by Our World In Data"
data_url = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"
column_description_url = r"https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-codebook.csv"


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
        "upstreamSource": data_url,
        "originalDataCollectionAgency": "https://systems.jhu.edu/",
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
### Compiled and aggregated by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University via Our World In Data

This dataset was created at {} and is usually updated once daily around 8am UTC from [the original dataset by our world in data]({}) which in turn sources the data from the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University
([more information on the process](https://ourworldindata.org/coronavirus-source-data)).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/")
""".format(now, data_url)


def get_data(url):
    dataframe = pandas.read_csv(url, low_memory=False)
    return dataframe


def get_column_descriptions():
    data = get_data(column_description_url)
    return {column: "{}. Source: {}".format(description, source) for column, description, source in zip(data["column"], data["description"], data["source"])}


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    description = get_description(now)
    column_descriptions = get_column_descriptions()
    data = get_data(data_url)
    metadata = get_metadata(now, [loc for loc in data.loc[:, "location"].unique()])
    create_or_update_dataset(name, metadata, description, data, column_descriptions)


if __name__ == "__main__":
    main()
