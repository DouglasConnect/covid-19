import requests
import pandas
import os
import tempfile
import datetime
from edelweiss_data import QueryExpression as Q

url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"

def get_metadata(now):
    today = datetime.datetime.now()
    # RKI data is updated around 8:00 CEST
    # RKI data is supposed to include cases until midnight CEST->22:00 UTC yesterday
    reporting_day = today - datetime.timedelta(days=1) if today.hour >= 8 else today - datetime.timedelta(days=2)
    estimated_reporting_cutoff = datetime.datetime(reporting_day.year, reporting_day.month, reporting_day.day, 22, tzinfo=datetime.timezone.utc)
    return { "datetimeRetrieved": "{}".format(now),
        "upstreamSource": url,
        "originalDataCollectionAgency": "https://www.rki.de",
        "dataBackgroundInformation": "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html",
        "estimatedReportingCutoff": "{}".format(estimated_reporting_cutoff),
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "by country"],
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    }

def get_description(now):
    return """This dataset was created at {}. It is updated once daily around 8:30 CEST from [the original dataset by the German Robert Koch Institut]({}) which gets the offial data once a day from the local health offices of the individual states.
([more information on the process](https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html)).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/")

Each dataset is only a snapshot of one day but by iterating through the versions of this dataset you can assemble time series.
        """.format(
            now, url
        )


def get_data():
    response = requests.get(url)
    response.raise_for_status()
    dataframes = pandas.read_html(response.text, flavor="bs4", thousands=".", decimal=",")
    df = dataframes[0]
    df.columns = ["State", "Confirmed cases", "Confirmed cases difference to previous day", "confirmed cases per 100.000 population", "Deaths"]
    df.iloc[-1, 0] = "Germany"
    return df


def upload_data(api, now, dataset, dataframe):
    try:
        with tempfile.TemporaryFile(mode="w+") as temp:
            dataframe.to_csv(temp, line_terminator="\n", index=False)
            temp.seek(0)
            dataset.upload_data(temp)
        dataset.infer_schema()
        dataset.upload_metadata(get_metadata(now))
        dataset.set_description(get_description(now))
        published_dataset = dataset.publish("First import on {}".format(now))
    except requests.HTTPError as err:
        print("not published: ", err.response.text)


def create_initial_dataset(api, name, now, dataframe):
    dataset = api.create_in_progress_dataset(name)
    upload_data(api, now, dataset, dataframe)


def update_dataset(api, name, now, dataframe):
    datasets_filter = Q.exact_search(Q.system_column("name"), name)
    datasets = api.get_published_datasets(condition=datasets_filter)
    if datasets.shape[1] != 1:
        raise Exception("Did not get exactly one dataset named {}".format(datasetname))
    published_dataset = datasets.iloc[0, -1]
    try:
        in_progress = api.get_in_progress_dataset(published_dataset.id)
        in_progress.delete()
    except:
        pass
    dataset = published_dataset.new_version()
    upload_data(api, now, dataset, dataframe)