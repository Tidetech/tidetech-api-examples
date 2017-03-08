#!/usr/bin/env python3

import json
import os
import sys

import requests

# Configuration of server and API Key
SERVER = 'https://api.stage.tidetech.xyz'     # Staging
# SERVER = 'http://api.tidetech.org'          # Production
API_KEY = os.environ.get('TIDETECH_API_KEY')  # Change this to your API key

if not API_KEY:
    print("Please set TIDETCH_API_KEY environment variable, or change it in this script. Terminating.")
    sys.exit()

HEADERS = {'Authentication': 'Token ' + API_KEY}
# Note that the API Key can be passed in as a query parameter with api_key=API_KEY

# The URLs of our Data API, including:
# Meta - get information about a dataset
meta_url = "{}/v1/data/{}/"
# Get data at one or more points (GET or POST)
point_url = "{}/v1/data/{}/point/"
# Get data for an area
area_url = "{}/v1/data/{}/area/"
# Multi-point allows requesting information from multiple datasets at once
multipoint_url = "{}/v1/data/points/"


def print_json(item):
    print(json.dumps(item, indent=4, separators=(',', ': ')))


# Get metadata for a single dataset.
def get_metadata(server, dataset, display=True):
    url = meta_url.format(server, dataset)
    response = requests.get(url, headers=HEADERS)
    file_info = response.json()

    if display:
        print_json(file_info)
    return file_info


# Get data for an area (returns NetCDF file)
def get_area(server, dataset, parameters, out_file):
    url = area_url.format(server, dataset)
    response = requests.get(url, headers=HEADERS, params=parameters)

    if response.status_code == 404 or response.status_code == 400:
        print("Area request failed... Reason follows.")
        print(response.text)
    else:
        with open(out_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


# Get data for one or more points, for a single dataset
def get_point(server, dataset, locations, out_file=None):
    url = point_url.format(server, dataset)

    parameters = {
        "locations": json.dumps(locations)
    }

    # response = requests.get(url, headers=HEADERS, params=parameters)
    # Or do a POST Request. POST is required for large numbers of points.
    response = requests.post(url, headers=HEADERS, json=parameters)

    result = response.json()

    # Write it to a file, if required, or print it, if not
    if response.status_code == 404 or response.status_code == 400:
        print("Area request failed... Reason follows.")
        print(response.text)
    else:
        if out_file:
            with open(out_file, 'w') as outfile:
                json.dump(result, outfile)
        else:
            print_json(result)


# Get data for one or more points for one or more datasets
def get_multipoints(server, datasets, locations, out_file=None):
    url = multipoint_url.format(server)

    parameters = {
        "locations": json.dumps(locations),
        "name": datasets
    }
    response = requests.get(url, headers=HEADERS, params=parameters)
    # Or do a POST Request. POST is required for large numbers of points.
    # response = requests.post(url, headers=HEADERS, json=parameters, params={'name': datasets})

    result = response.json()

    # Write it to a file, if required, or print it, if not
    if response.status_code == 404 or response.status_code == 400:
            print("Area request failed... Reason follows.")
            print(response.text)
    else:
        if out_file:
            with open(out_file, 'w') as outfile:
                json.dump(result, outfile)
        else:
            print_json(result)


def get_example_metadata():
    print("Getting metadata")
    dataset = 'global_combined_currents'
    get_metadata(SERVER, dataset, display=True)


# An example area, used in testing
def get_example_area():
    print("Getting area dataset")
    # Area parameters
    dataset = 'global_waves'
    minX = 100
    maxX = 102
    minY = 10
    maxY = 12
    start_date = '2016-02-01T00:00'
    end_date = '2016-02-23T2:00'

    region = {
        "type": "Polygon",
        "coordinates":
            [[
                [minX, minY],
                [minX, maxY],
                [maxX, maxY],
                [maxX, minY],
                [minX, minY]
            ]]
    }

    parameters = {
        "region": json.dumps(region),
        "start_datetime": start_date,
        "end_datetime": end_date,
        "filename": "ThisIsATest"
    }
    get_area(SERVER, dataset, parameters, '/tmp/test_waves.nc')


# An example point, used in testing
def get_example_point():
    print("Getting points from a single dataset")
    dataset = 'global_combined_currents'
    locations = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [144, 36]},
                "properties": {
                    "id": 'p1',
                    # "codes": '49,50',  # Optional
                    "datetime": '2016-02-01T00:00'
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [144, 37]},
                "properties": {
                    "id": 'p2',
                    # "codes": '49,50',   # Optional
                    "datetime": '2016-02-01T12:00'
                }
            }
        ]
    }
    get_point(SERVER, dataset, locations, out_file='/tmp/test_waves.json')


# An example multi-dataset point, used in testing
def get_example_multipoints():
    print("Getting points from multiple datasets")
    datasets = 'global_combined_currents,global_wind,global_waves'
    locations = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [19, -40]},
                "properties": {
                    "id": 'p3',
                    # "codes": '49,50,33,34,8',  # Optional
                    "datetime": '2016-06-20T18:00'
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [20, -41]},
                "properties": {
                    "id": 'p4',
                    # "codes": '49,50,33,34,8',  # Optional
                    "datetime": '2016-06-20T21:00'
                }
            }
        ]
    }
    get_multipoints(SERVER, datasets, locations, out_file='/tmp/test_all.json')


# Run the examples here.
def run_examples():
    get_example_metadata()
    get_example_area()
    # ncdump -h /tmp/test_waves.nc
    get_example_point()
    # ogrinfo -al /tmp/test_waves.json
    get_example_multipoints()
    # ogrinfo -al /tmp/test_all.json


if __name__ == '__main__':
    run_examples()
