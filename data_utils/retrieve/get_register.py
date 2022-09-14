import requests
import os

CHADWICK_PEOPLE_REGISTER_URL = "https://github.com/chadwickbureau/register/raw/master/data/people.csv"

# get a list of CSV files from the data directory


def get_csv_files():
    csv_files = []
    for file in os.listdir("../data"):
        if file.endswith(".csv"):
            csv_files.append(file)
    return csv_files


def get_register():
    # get the CSV file from the Chadwick people register
    response = requests.get(CHADWICK_PEOPLE_REGISTER_URL)
    return response.text


def write_register(register):
    # write the CSV file to the data directory
    with open("../data/people.csv", "w+") as f:
        f.write(register)


register = get_register()
write_register(register)
