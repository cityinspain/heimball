import pandas as pd

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url="http://localhost:4000/graphql")
client = Client(transport=transport)

df = pd.read_csv("data/mlb_people.csv", dtype={
    "mlb_id": str,
    "birth_city": str,
    "birth_state_province": str,
    "birth_country": str,
    "birth_date": str,
})

df = df.fillna("")

for index, row in df.iterrows():
    mlb_id = row['mlb_id']
    birth_city = row['birth_city']
    birth_state_province = row['birth_state_province']
    birth_country = row['birth_country']
    birth_date = row['birth_date']
    name = row['name']
    first_name = row['first_name']
    last_name = row['last_name']
    height = row['height']
    weight = row['weight']

    mutation = gql(
        """
        mutation(
            $mlbId: String,
            $name: String,
            $firstName: String,
            $lastName: String,
            $birthDate: Date,
            $birthCity: String,
            $birthStateProvince: String,
            $birthCountry: String,
            $height: Int,
            $weight: Int,
            ) {
                createPlayer(
                    mlbId: $mlbId,
                    name: $name,
                    firstName: $firstName
                    lastName: $lastName
                    birthDate: $birthDate
                    birthStateProvince: $birthStateProvince
                    birthCountry: $birthCountry
                    birthCity: $birthCity
                    height: $height
                    weight: $weight

                ) {
                    mlbId
                }
            
        }
        """
    )

    try:
        params = {
            "mlb_id": mlb_id,
            "birth_city": birth_city,
            "birth_state_province": birth_state_province,
            "birth_country": birth_country,
            "birth_date": birth_date,
            "mlbId": mlb_id,
            "name": name,
            "firstName": first_name,
            "lastName": last_name,
            "birthDate": birth_date,
            "birthCity": birth_city,
            "birthStateProvince": birth_state_province,
            "birthCountry": birth_country,
            "height": height,
            "weight": weight,
        }
        result = client.execute(mutation, variable_values=params)
        print(result)
    except Exception as e:
        print(e)
