import requests

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import date

transport = AIOHTTPTransport(url="http://localhost:4001/graphql")
client = Client(transport=transport)

query = gql(
    """
    query ExampleQuery($parentOrgId: String) {

  allRankedProspectsByParentOrgId(parentOrgId: $parentOrgId) {
    id
    name
    mlbId
    fangraphsOrgProspectRanking
    fangraphsOverallProspectRanking
  }
# allRankedProspectsByParentOrgId(parentOrgId: "136") {
  #   mlbId
  #   name
  #   fangraphsOrgProspectRanking
  # }
}
""")

result = client.execute(
    query,
    variable_values={"parentOrgId": "136"}
)

ids = [int(player["mlbId"])
       for player in result["allRankedProspectsByParentOrgId"]]


def get_all_teams_ids_by_parent_id(parent_id):
    url = "https://statsapi.mlb.com/api/v1/teams?sportIds=1,11,12,13,14&season=2022"
    response = requests.get(url)
    data = response.json()
    teams = data.get('teams', [])
    return [(team.get('id'), team.get("sport", {}).get("id", None)) for team in teams if team.get('parentOrgId') == parent_id or team.get('id') == parent_id]


today = date.today()
most_recent_game_pks = []
for team in get_all_teams_ids_by_parent_id(136):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId={team[1]}&teamId={team[0]}&season=2022&fields=dates,date,games,gamePk"
    response = requests.get(url)
    data = response.json()
    dates = data.get('dates', [])

    # find the most recent date
    most_recent_date = None
    most_recent_game_pk = None
    for d in dates:
        if date.fromisoformat(d.get('date', None)) >= today:
            break
        if most_recent_date is None or d.get('date') > most_recent_date:
            most_recent_date = d.get('date')
            most_recent_game_pk = d.get('games')[0].get('gamePk')

    # print(most_recent_date)
    most_recent_game_pks.append(most_recent_game_pk)

player_stats = []

for game_pk in most_recent_game_pks:
    # print(game_pk)
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    # print(url)
    response = requests.get(url)
    data = response.json()

    teams = data.get('teams', {})
    for team in teams.values():
        players = team.get('players', {})
        # print(players)
        for player in players.values():
            # print(player)
            if player.get('person', {}).get('id', None) in ids:
                # print('in ids')
                player_stats.append(player)

    # print(data)

print(player_stats)
print(len(player_stats))
for player in player_stats:
    person = player.get('person', {})
    name = person.get('fullName', None)

    pos_abbreviation = player.get('position', {}).get('abbreviation', None)
    pos_code = player.get('position', {}).get('code', None)
    batting_stats = player.get('stats', {}).get('batting', {})
    pitching_stats = player.get('stats', {}).get('pitching', {})

    print(f"{name} - {pos_abbreviation}")
    print(batting_stats)
    print(pitching_stats)
# for player in result["allRankedProspectsByParentOrgId"]:
#     url = f"https://statsapi.mlb.com/api/v1/people/{player['mlbId']}?hydrate=stats(group=[pitching,hitting],type=[gameLog])"
#     response = requests.get(url)
#     data = response.json()

#     print(data)
