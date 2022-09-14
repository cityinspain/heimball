import requests
import os

CHADWICK_PEOPLE_REGISTER_URL = "https://github.com/chadwickbureau/register/raw/master/data/people.csv"

def get_register():
    # get the CSV file from the Chadwick people register
    response = requests.get(CHADWICK_PEOPLE_REGISTER_URL)
    return response.text