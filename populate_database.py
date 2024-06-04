from os import listdir
from os.path import join, isdir
from requests.auth import HTTPBasicAuth
import requests
import argparse


URL = ""
auth = None


def linebreak(length):
    tmp = "=" * length
    print(tmp)


def parse_datum(filepath):
    """ Fetches coordinates from datum file """
    datum_path = join(filepath, "datum.yaml")
    with open(datum_path, "r", encoding="utf-8") as file:
        file_lines = [_.strip() for _ in file.readlines()]

    latittude = search_file("datum_latitude", file_lines)
    longitude = search_file("datum_longitude", file_lines)

    if latittude is None or longitude is None:
        print("Couldn't find coordinates in file.")
        return
    
    if "#" in latittude:
        latittude = latittude.split("#")[0].strip()
    if "#" in longitude:
        longitude = longitude.split("#")[0].strip()

    latittude = float(latittude.split(" ")[-1].strip())
    longitude = float(longitude.split(" ")[-1].strip())
    return latittude, longitude


def search_file(word, contents):
    """ Searches for a word in a file """
    for line in contents:
        if word in line:
            return line
    return None


def parse_customer(filepath, customer):
    """Parses Customers in ThorvaldAutonomyConfigs"""

    data = {
        'customer': customer
    }
    response = requests.post(URL + "/start-time/add/customer", json=data, auth=auth)
    if response.status_code == 201:
        print(f"Added {data['customer']} to database")
    else:
        print(f"{data['customer']} already in database, skipping")  


    for site in listdir(filepath):
        if isdir(filepath):
            parse_site(join(filepath, site), site, customer)


def parse_site(filepath, site, customer):
    """Parses Sites in ThorvaldAutonomyConfigs"""

    data = {
        'customer': customer,
        'site': site
    }

    response = requests.post(URL + "/start-time/add/site", json=data, auth=auth)
    if response.status_code == 201:
        print(f"Added {data['site']} to database")
    else:
        print(f"{data['site']} already in database, skipping")


    for field in listdir(filepath):
        new_filepath = join(filepath, field)
        if isdir(new_filepath):
            parse_field(new_filepath, field, site, customer)


def parse_field(filepath, field, site, customer):
    """Parses Fields in ThorvaldAutonomyConfigs"""

    lat, lng = parse_datum(filepath)

    data = {
        'field': field,
        'site': site,
        'customer': customer,
        'lat': lat,
        'lng': lng
    }

    response = requests.post(URL + "/start-time/add/field", json=data, auth=auth)
    if response.status_code == 201:
        print(f"Added {data['field']} to database")
    else:
        print(f"{data['field']} already in database, skipping")


def main():
    """Scans for new map files in ThorvaldAutonomyConfigs"""
    global auth
    global URL

    map_root = "ThorvaldAutonomyConfigs/thorvald_autonomy_configs/config/site_files/"
    welcome_string = "= Treatment Planner Populator ="

    parser = argparse.ArgumentParser(description="Populate database for ThorvaldAutonomy.")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--password", required=True, help="Password for authentication")
    parser.add_argument("--url", required=True, help="Base URL of the API")

    args = parser.parse_args()

    linebreak(len(welcome_string))
    print(welcome_string)
    linebreak(len(welcome_string))

    auth = HTTPBasicAuth(args.username, args.password)
    URL = args.url

    for file in listdir(map_root):
        if isdir(join(map_root, file)):
            parse_customer((join(map_root, file)), file)


if __name__ == "__main__":
    main()