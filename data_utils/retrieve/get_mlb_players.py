import requests
from datetime import date
from util.get_all_teams import get_pro_teams_from_mlb_api
from util.fix_height import convert_height_string_to_inches

import pandas as pd


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

    }


def get_team_40_man_roster(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?rosterType=40Man&hydrate=person"
    res = requests.get(url)
    data = res.json()

    roster = data['roster']

    return [map_player(player) for player in roster]


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


players_df = get_via_teams()
players_df.to_csv("data/mlb_people.csv", index=False)
