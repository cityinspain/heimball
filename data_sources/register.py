import requests

import pandas as pd
import numpy as np
import datetime
import sqlite3 as db


from util import convert_height_string_to_inches, get_pro_teams_from_mlb_api,  map_fangraphs_api_player, strip_accents

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url="http://localhost:4000/graphql")
client = Client(transport=transport)


CHADWICK_PEOPLE_REGISTER_URL = "https://github.com/chadwickbureau/register/raw/master/data/people.csv"


def get_register():
    # get the CSV file from the Chadwick people register
    response = requests.get(CHADWICK_PEOPLE_REGISTER_URL)
    return response.text


INT_THEN_STRING_COLUMNS = ['key_mlbam', 'key_fangraphs']
STRING_KEY_COLUMNS = ["key_retro", "key_bbref", "key_bbref_minors"]
DISCARD_COLUMNS = [
    "key_npb", "key_sr_nfl", "key_sr_nhl", "key_sr_nba", 'key_findagrave',
    'pro_managed_first', 'pro_managed_last', 'mlb_managed_first', 'mlb_managed_last', 'col_managed_first', 'col_managed_last',
    'pro_umpired_first', 'pro_umpired_last', 'mlb_umpired_first', 'mlb_umpired_last'
]
INT64_COLUMNS = [
    'birth_year', 'birth_month', 'birth_day',
    'death_year', 'death_month', 'death_day',
    'pro_played_first', 'pro_played_last',
    'mlb_played_first', 'mlb_played_last',
    'col_played_first', 'col_played_last'
]
rename = {
    'key_retro': 'retro_id',
    'key_bbref': 'bbref_id',
    'key_bbref_minors': 'bbref_minors_id',
    'key_mlbam': 'mlb_id',
    'key_fangraphs': 'fangraphs_id',
    'key_uuid': 'register_uuid',
    'key_person': 'register_id',
}


def create_birth_date(row):
    birth_year = row['birth_year']
    birth_month = row['birth_month']
    birth_day = row['birth_day']

    if pd.isna(birth_year) or pd.isna(birth_month) or pd.isna(birth_day):
        return None
    else:
        return datetime.date(birth_year, birth_month, birth_day)


def combine_name(row):
    first = row['name_first']
    last = row['name_last']
    if pd.isna(first):
        return ""
    if pd.isna(last):
        return ""

    return first + ' ' + last


def set_active(row):
    if row['pro_played_last'] == datetime.date.today().year:
        return True
    else:
        return False


def retrieve_and_process_register():

    df = pd.read_csv(CHADWICK_PEOPLE_REGISTER_URL)

    df = df.drop(DISCARD_COLUMNS, axis=1)

    # remove players who never played pro ball
    df = df[~df['pro_played_first'].isnull()]

    # convert floats to truncated strings, replacing nulls with empty string
    for column in INT_THEN_STRING_COLUMNS:
        df[column] = df[column].fillna(0)
        df[column] = df[column].astype(int)
        df[column] = df[column].astype(str)
        df[column] = df[column].replace('0', '')

    # convert key_retro, key_bbref, key_bbref_minors to string
    # replacing null values with empty string
    for column in STRING_KEY_COLUMNS:
        df[column] = df[column].fillna('')
        df[column] = df[column].astype(str)

    for column in INT64_COLUMNS:
        df[column] = df[column].astype('Int64')

    # create birth_date column, and fill in missing values

    # name info from register seems inaccurate, so we'll assign it to a different property
    # may be useful, but we'll prefer the name according to the MLB API.
    df['register_name'] = df.apply(combine_name, axis=1)
    df.drop(['name_first', 'name_last', 'name_given', 'name_suffix',
            'name_matrilineal', 'name_nick'], axis=1, inplace=True)

    # assign birth_date column, returning None if not all values are present
    # drop birth_month and birth_day either way - inaccurate data will be lost here
    df['birth_date'] = df.apply(create_birth_date, axis=1)
    df.drop(['birth_month', 'birth_day'], axis=1, inplace=True)

    # assign active column according to pro_played_last
    df['register_active'] = df.apply(set_active, axis=1)

    # rename columns in df according to rename dict
    df.rename(columns=rename, inplace=True)

    cnx = db.connect('data/register.db')
    df.to_sql('register', cnx, if_exists='replace', index=False)
    cnx.close()


def map_player(player):
    person = player['person']

    player_id = person.get('id')
    player_name = person.get('fullName', None)

    player_first_name = person.get('firstName', None)
    player_last_name = person.get('lastName', None)
    player_use_name = person.get('useName', None)

    player_birth_date = person.get('birthDate', None)
    # if player_birth_date:
    #     player_birth_date = date.fromisoformat(player_birth_date)

    player_birth_city = person.get('birthCity', None)
    player_birth_state_province = person.get('birthStateProvince', None)
    player_birth_country = person.get('birthCountry', None)

    player_height = person.get('height', None)
    player_weight = person.get('weight', None)

    parent_team_id = player.get('parentTeamId', None)

    if player_height:
        player_height = convert_height_string_to_inches(player_height)

    return {
        'mlb_id': player_id,
        'name': player_name,
        'first_name': player_first_name,
        'last_name': player_last_name,
        'use_name': player_use_name,
        'birth_date': player_birth_date,
        'birth_city': player_birth_city,
        'birth_state_province': player_birth_state_province,
        'birth_country': player_birth_country,
        'height': player_height,
        'weight': player_weight,
        "parent_team_id": parent_team_id
    }


def get_team_40_man_roster(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?rosterType=40Man&hydrate=person"
    res = requests.get(url)
    data = res.json()

    roster = data['roster']

    players = [map_player(player) for player in roster]
    # players = map(lambda p: {**p, 'team_id': team_id}, players)
    return list(players)


def get_via_teams():
    teams = get_pro_teams_from_mlb_api()
    num_teams = len(teams)
    counter = 0
    ids = [team['id'] for team in teams]
    all_players = []
    for team_id in ids:
        counter += 1
        print(
            f"retrieving 40 man roster for team: {str(team_id).ljust(6)} ({counter}/{num_teams})")
        roster = get_team_40_man_roster(team_id)
        all_players.extend(roster)

    return pd.DataFrame(all_players)


def get_and_process_from_mlb():
    players_df = get_via_teams()
    # players_df.to_csv("data/mlb_people.csv", index=False)

    for index, row in players_df.iterrows():
        mlb_id = str(row['mlb_id'])
        birth_city = row['birth_city']
        birth_state_province = row['birth_state_province']
        birth_country = row['birth_country']
        birth_date = row['birth_date']
        name = row['name']
        first_name = row['first_name']
        last_name = row['last_name']
        height = row['height']
        weight = row['weight']
        team_id = str(row['parent_team_id'])

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
                $parentOrgId: String
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
                        parentOrgId: $parentOrgId
                    ) {
                        mlbId
                    }
                
            }
            """
        )

        update_mutation = gql(
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
                $parentOrgId: String
                ) {
                    updatePlayerByMlbId(
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
                        parentOrgId: $parentOrgId
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
                "parentOrgId": team_id
            }
            result = client.execute(mutation, variable_values=params)
            print(f'created player: {mlb_id}, {name}')
        except Exception as e:
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
                    "parentOrgId": team_id
                }
                result = client.execute(
                    update_mutation, variable_values=params)
                # print(result)
                print(f'updated player: {mlb_id} ({name})')
            except Exception as e2:
                pass
            # print(e)


def reset_all_fangraphs_prospect_rankings():
    query = gql(
        """
            query {
                allPlayers {
                    id
                }
        }""")

    result = client.execute(query)
    players = result['allPlayers']
    for player in players:
        player_id = player['id']
        mutation = gql(
            """
            mutation($playerId: ID!) {
                updatePlayerById(
                    id: $playerId,
                    fangraphsProspectRanking: null
                ) {
                    id
                }
            }
            """
        )
        result = client.execute(mutation, variable_values={
                                "playerId": player_id})
        print(f"reset fangraphs prospect ranking for player: {player_id}")

    # result = client.execute(mutation)


def get_and_process_fangraphs_prospects():
    url = "https://cdn.fangraphs.com/api/prospects/board/prospects-list?statType=player&draft=2022updated&valueHeader=prospect-2022"

    response = requests.get(url)
    data = response.json()

    players = list(map(map_fangraphs_api_player, data))

    for player in players:

        all_by_name = gql(
            """
            query($name: String!) {
                playersByName(
                    name: $name
                ) {
                    id
                    name
                    birthDate
                    mlbId

                }
            }
            """)

        result = client.execute(
            all_by_name,
            variable_values={
                "name": player['playerName']
            }
        )

        players = result['playersByName']

        if len(players) == 1:
            player_id = players[0]['id']
            mlb_id = players[0]['mlbId']
            birth_date = players[0]['birthDate']
            player_name = players[0]['name']

            if birth_date == player['birthDate']:
                mutation = gql(
                    """
                    mutation(
                        $mlbId: String!,
                        $fangraphsMinorMasterId: String,
                        $fangraphsOrgProspectRanking: Int,
                        $fangraphsOverallProspectRanking: Int
                        ) {
                        updatePlayerByMlbId(
                            mlbId: $mlbId,
                            fangraphsMinorMasterId: $fangraphsMinorMasterId
                            fangraphsOrgProspectRanking: $fangraphsOrgProspectRanking
                            fangraphsOverallProspectRanking: $fangraphsOverallProspectRanking
                        ) {
                            id
                        }
                    }
                    """
                )
                result = client.execute(
                    mutation,
                    variable_values={
                        "mlbId": mlb_id,
                        "fangraphsMinorMasterId": player.get("minorMasterId", None),
                        "fangraphsOrgProspectRanking": player.get('orgRank', None),
                        "fangraphsOverallProspectRanking": player.get('ovrRank', None)
                    })
                print(
                    f"updated fangraphs prospect ranking for player: {player_name} ({mlb_id})")
            else:
                print(
                    f"birth dates don't match for player: {player_name} ({mlb_id})")

        if len(players) == 0:
            print(f"no players found for {player['playerName']}")
            continue

        if len(players) > 1:

            matching_player = None
            for player in players:
                if player['birthDate'] == player['birthDate']:
                    if matching_player:
                        continue
                        # raise Exception(
                        #     'multiple players found with name and birth date')
                    matching_player = player

            if matching_player:
                mutation = gql(
                    """
                    mutation(
                        $mlbId: String!,
                        $fangraphsMinorMasterId: String,
                        $fangraphsOrgProspectRanking: Int,
                        $fangraphsOverallProspectRanking: Int
                        ) {
                        updatePlayerByMlbId(
                            mlbId: $mlbId,
                            fangraphsMinorMasterId: $fangraphsMinorMasterId
                            fangraphsOrgProspectRanking: $fangraphsOrgProspectRanking
                            fangraphsOverallProspectRanking: $fangraphsOverallProspectRanking
                        ) {
                            id
                        }
                    }
                    """
                )
                result = client.execute(
                    mutation,
                    variable_values={
                        "mlbId": matching_player["mlbId"],
                        "fangraphsMinorMasterId": player.get("minorMasterId", None),
                        "fangraphsOrgProspectRanking": player.get('orgRank', None),
                        "fangraphsOverallProspectRanking": player.get('ovrRank', None)
                    })
                print(
                    f"updated fangraphs prospect ranking for player: {player_name} ({mlb_id})")

        # local_api_url = f"http://localhost:3000/search?firstName={player['firstName']}&lastName={player['lastName']}&birthDate={player['birthDate']}&fullName={player['playerName']}"
        # query = gql(
        #     """
        #     query($birthDate: Date!) {
        #         allPlayersByBirthDate(

        #             birthDate: $birthDate
        #             ) {
        #                 mlbId
        #                 name
        #                 firstName
        #                 lastName
        #             }
        #     }
        #     """)

        # variables = {
        #     "birthDate": player["birthDate"]
        # }

        # result = client.execute(query, variable_values=variables)
        # all_players = result['allPlayersByBirthDate']

        # if len(all_players) == 1:
        #     pass
        # else:
        #     fg_player_first_name = strip_accents(player["firstName"])
        #     fg_player_last_name = strip_accents(player["lastName"])

        #     matching_player = None

        #     potential_matches = []
        #     for api_player in all_players:
        #         api_player_first_name = strip_accents(api_player["firstName"])
        #         api_player_last_name = strip_accents(api_player["lastName"])

        #         if fg_player_last_name == api_player_last_name or fg_player_first_name == api_player_first_name:
        #             potential_matches.append(api_player)

        #         if len(potential_matches) == 1:
        #             matching_player = potential_matches[0]
        #             break
        #         elif len(potential_matches) > 1:
        #             print(
        #                 f"could not match player(s) with birth date {player['birthDate']}. possible matches:")
        #             for api_player in all_players:
        #                 print(f"{api_player['name']}")

        #     if not matching_player:
        #         print('match failed: ' + player['playerName'])
        #     else:
        #         update_mutation = gql(
        #             """

        #             mutation(
        #                 $mlbId: String,
        #                 $fangraphsMinorMasterId: String,
        #                 $fangraphsOrgProspectRanking: Int,
        #                 $fangraphsOverallProspectRanking: Int
        #                 ) {
        #                 updatePlayerByMlbId(
        #                     mlbId: $mlbId
        #                     fangraphsMinorMasterId: $fangraphsMinorMasterId
        #                     fangraphsOrgProspectRanking: $fangraphsOrgProspectRanking
        #                     fangraphsOverallProspectRanking: $fangraphsOverallProspectRanking
        #                 ) {
        #                     mlbId
        #                 }
        #             }""")

        #         variables = {
        #             "mlbId": matching_player["mlbId"],
        #             "fangraphsMinorMasterId": player["minorMasterId"],
        #             "fangraphsOrgProspectRanking": player["orgRank"],
        #             "fangraphsOverallProspectRanking": player["ovrRank"]
        #         }

        #         result = client.execute(
        #             update_mutation, variable_values=variables)


# get_and_process_from_mlb()
# reset_all_fangraphs_prospect_rankings()
get_and_process_fangraphs_prospects()
# df.to_csv('data/people_processed.csv', index=False)

# only_active = df[df['pro_played_last'] == datetime.date.today().year]
# only_active.to_csv('data/people_processed_active.csv', index=False)
