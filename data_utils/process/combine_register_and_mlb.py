import pandas as pd

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url="http://localhost:4000/graphql")
client = Client(transport=transport)

df_register = pd.read_csv("data/people_processed.csv", dtype={
    "retro_id": str,
    "bbref_id": str,
    "bbref_minors_id": str,
    "mlb_id": str,
    "fangraphs_id": str,
    "register_uuid": str,
    "register_id": str,
    "birth_year": str,
    "birth_date": str,
    "birth_state_province": str,
    "birth_country": str,
    "birth_city": str

})
df_mlb = pd.read_csv("data/mlb_people.csv", dtype={
    "mlb_id": str,
    "birth_city": str,
    "birth_state_province": str,
    "birth_country": str,
    "birth_date": str,
})

df_register = df_register.fillna("")
df_mlb = df_mlb.fillna("")
# df_register['birth_state_province'].fillna("", inplace=True)

df = pd.merge(df_register, df_mlb, on="mlb_id")
print(df.columns)

df.rename({"birth_date_y": "birth_date"}, axis=1, inplace=True)

KEEP_COLUMNS = [
    "name",
    "mlb_id",
    "register_id",
    "retro_id",
    "bbref_id",
    "bbref_minors_id",
    "fangraphs_id",
    "first_name",
    "last_name",
    "use_name",
    'birth_date',
    'birth_year',
    'birth_city',
    'birth_state_province',
    'birth_country',
    "height",
    "weight",
]

df = df[KEEP_COLUMNS]

# df.to_csv("data/combined_people.csv", index=False)

for index, row in df.iterrows():
    query = gql(
        """
        mutation(
            $mlbId: String,
            $name: String,
            $firstName: String,
            $lastName: String,
            $birthDate: Date,
            $bbrefId: String,
            $bbrefMinorsId: String,
            $retroId: String,
            $fangraphsId: String,
            $birthStateProvince: String,
            $birthCountry: String,
            $birthCity: String,
            $height: Int,
            $weight: Int,
            ) {
                createPlayer(
                    mlbId: $mlbId,
                    bbrefId: $bbrefId
                    bbrefMinorsId: $bbrefMinorsId
                    retroId: $retroId
                    fangraphsId: $fangraphsId
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

    variables = {
        'mlbId': str(row['mlb_id']),
        'bbrefId': row['bbref_id'],
        'fangraphsId': str(row['fangraphs_id']),
        'firstName': row['first_name'],
        'lastName': row['last_name'],
        'birthDate': row['birth_date'],
        'name': row['name'],
        'retroId': row['retro_id'],
        'bbrefMinorsId': row['bbref_minors_id'],
        'birthStateProvince': row['birth_state_province'],
        'birthCountry': row['birth_country'],
        'birthCity': row['birth_city'],
        'height': row['height'],
        'weight': row['weight'],

    }

    try:
        result = client.execute(query, variable_values=variables)
    except Exception as e:
        print(e)
        print(row)
        continue
