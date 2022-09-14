import unicodedata
import requests
from datetime import datetime, timedelta


# convert height formatted as "feet' inches"" to inches
def convert_height_string_to_inches(height_string):

    feet_str = height_string.split("'")[0]

    inches_str = height_string.split("'")[1].split('"')[0]

    feet = int(feet_str)
    inches = int(inches_str)

    return feet * 12 + inches


def __map_team(team):

    parent_org_name = team.get('parentOrgName', None)
    parent_org_id = team.get('parentOrgId', None)

    league_id = team.get('league', {}).get('id', None)
    division_id = team.get('division', {}).get('id', None)
    sport_id = team.get('sport', {}).get('id', None)

    return {
        'id': team.get('id', None),
        'name': team.get('name', None),
        'locationName': team.get('locationName', None),
        'teamName': team.get('teamName', None),
        'abbreviation': team.get('abbreviation', None),
        'parentOrgName': parent_org_name,
        'parentOrgId': parent_org_id,
        'leagueId': league_id,
        'divisionId': division_id,
        'sportId': sport_id,
    }


def get_pro_teams_from_mlb_api():
    this_year = datetime.now().year
    # sport ids 1,11,12,13,14 refer to MLB, AAA, AA, A+, and A
    url = f"https://statsapi.mlb.com/api/v1/teams?sportIds=1,11,12,13,14&season={this_year}"

    response = requests.get(url)
    data = response.json()

    teams = data.get('teams', [])
    return [__map_team(team) for team in teams]


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def map_fangraphs_api_player(player):
    base_date = "1899-12-30"
    base_date = datetime.strptime(base_date, "%Y-%m-%d")

    minorMasterId = player.get("minorMasterId", None)
    playerName = player["playerName"]
    playerId = player.get("ID", None)
    ovrRank = player.get("Ovr_Rank", None)
    orgRank = player.get("Org_Rank", None)

    firstName = player.get("FirstName", None)
    lastName = player.get("LastName", None)

    birth_date_delta = int(player["BirthDate"])
    birth_date = base_date + timedelta(days=birth_date_delta)
    birth_date = birth_date.strftime("%Y-%m-%d")

    return {
        "minorMasterId": minorMasterId,
        "playerName": playerName,
        "firstName": firstName,
        "lastName": lastName,
        "playerId": playerId,
        "ovrRank": ovrRank,
        "orgRank": orgRank,
        "birthDate": birth_date,
    }
