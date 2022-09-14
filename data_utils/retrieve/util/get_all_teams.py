import requests
from datetime import datetime


def map_team(team):

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
    return [map_team(team) for team in teams]
