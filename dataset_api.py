#!/usr/bin/env python

import json
import os
import sys
import tempfile

from datetime import datetime

import requests

from tidetech_methods import print_json, save_file

# Configuration of server and API Key
SERVER = 'https://api.tidetech.org'

# Change this to your API key
API_KEY = os.environ.get('TIDETECH_API_KEY')

if not API_KEY:
    print("Please set TIDETCH_API_KEY environment variable, or change it in this script. Terminating.")
    sys.exit()

# Note that the API Key can be passed in as a query parameter with api_key=API_KEY
HEADERS = {'Authentication': 'Token ' + API_KEY}

# The URLs of our Data API, including:
dataset_url = "{}/v1/dataset/"

# Single dataset metadata
dataset_meta_url = "{}/v1/dataset/{}"

# Get a dataset, including subsetting
dataset_data_url = "{}/v1/dataset/{}/data/"

# Get data at one or more points (GET or POST)
point_url = "{}/v1/dataset/{}/point/"


# Get a list of all the datasets, including metadata
def get_dataset_list(server, display=True):
    url = dataset_url.format(server)
    response = requests.get(url, headers=HEADERS)
    dataset_info = response.json()

    if display:
        print_json(dataset_info)
    return dataset_info


# Get a list of all the datasets, including metadata
def get_dataset_info(server, dataset_name, display=True):
    url = dataset_meta_url.format(server, dataset_name)
    response = requests.get(url, headers=HEADERS)
    dataset_info = response.json()

    if display:
        print_json(dataset_info)
    return dataset_info


# Download a dataset, including subsetting.
def get_dataset_download(server, dataset_name, parameters, out_file):
    url = dataset_data_url.format(server, dataset_name)
    response = requests.get(url, params=parameters, headers=HEADERS)

    save_file(response, out_file)


# Get data for one or more points, for a single dataset
def get_point(server, dataset, locations, out_file=None):
    url = point_url.format(server, dataset)

    parameters = {
        "locations": json.dumps(locations)
    }

    response = requests.get(url, headers=HEADERS, params=parameters)
    # Or do a POST Request. POST is required for large numbers of points.
    # response = requests.get(url, headers=HEADERS, json=parameters)

    result = response.json()

    # Write it to a file, if required, or print it, if not
    if response.status_code != 200:
        print("Area request failed... Reason follows.")
        print(response.text)
    else:
        if out_file:
            with open(out_file, 'w') as outfile:
                json.dump(result, outfile)
        else:
            print_json(result)


def get_example_datasets_info():
    print("Listing information on all available datasets")
    get_dataset_list(SERVER)


def get_example_dataset_info():
    print("Listing information on a single dataset")
    dataset = 'global-combined-currents'
    get_dataset_info(SERVER, dataset)


def get_example_dataset_download():
    print("Downloading a zipped grib file")
    dataset = 'bass-strait-currents'

    # The minimum requirement for parameters is file_format. Generally you want to download a zipped file too.
    # Note that you will be redirected to a temporary S3 URL. If you don't want this, use no_redirect: True.
    parameters = {
        'file_format': 'grb',  # This can be nc for NetCDF
        'zipped': True
    }

    out_file = os.path.join(tempfile.mkdtemp(), '{}.grb.bz2'.format(dataset))
    print("Saving file to {}".format(out_file))
    get_dataset_download(SERVER, dataset, parameters, out_file)


def get_example_dataset_download_subset_geo():
    print("Downloading a zipped grib file")
    dataset = 'bass-strait-currents'

    # Bounds is minx, miny, maxx, maxy
    parameters = {
        'file_format': 'grb',  # This can be nc for NetCDF
        'zipped': True,
        'bounds': '145.8545,-41.2447,149.392,-39.0278'
    }

    out_file = os.path.join(tempfile.mkdtemp(), '{}.grb.bz2'.format(dataset))
    print("Saving file to {}".format(out_file))
    get_dataset_download(SERVER, dataset, parameters, out_file)


def get_example_dataset_download_subset_time():
    print("Downloading a zipped grib file")
    dataset = 'bass-strait-currents'

    # first get info
    file_info = get_dataset_info(SERVER, dataset, display=False)
    timestep1 = file_info['timesteps'][0]
    timestep2 = file_info['timesteps'][10]

    # time_from to time_to. You can also use timsesteps=1,2,3 to get the first 3, for example.
    parameters = {
        'file_format': 'grb',  # This can be nc for NetCDF
        'zipped': True,
        'time_from': timestep1,
        'time_to': timestep2
    }

    out_file = os.path.join(tempfile.mkdtemp(), '{}.grb.bz2'.format(dataset))
    print("Saving file to {}".format(out_file))
    get_dataset_download(SERVER, dataset, parameters, out_file)


# An example point, used in testing
def get_example_point():
    print("Getting points from a single dataset")
    dataset = 'global-combined-currents'
    locations = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [144, 36]},
                "properties": {
                    "id": 'p1',
                    # "codes": '49,50',  # Optional
                    "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M")
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [144, 37]},
                "properties": {
                    "id": 'p2',
                    # "codes": '49,50',   # Optional
                    "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M")
                }
            }
        ]
    }

    out_file = os.path.join(tempfile.mkdtemp(), 'test_currents.json')
    print("Saving file to {}".format(out_file))
    get_point(SERVER, dataset, locations, out_file=out_file)


# Run the examples here.
def run_examples():
    get_example_datasets_info()
    get_example_dataset_info()
    get_example_dataset_download()
    get_example_dataset_download_subset_geo()
    get_example_dataset_download_subset_time()
    get_example_point()


if __name__ == '__main__':
    run_examples()
