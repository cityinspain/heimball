import requests
from datetime import timedelta, date, datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import unicodedata

transport = AIOHTTPTransport(url="http://localhost:4000/graphql")
client = Client(transport=transport)


url = "https://cdn.fangraphs.com/api/prospects/board/prospects-list?statType=player&draft=2022updated&valueHeader=prospect-2022"

response = requests.get(url)
data = response.json()

base_date = "1899-12-30"
base_date = datetime.strptime(base_date, "%Y-%m-%d")


def map_response(player):

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


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


players = list(map(map_response, data))

for player in players:

    # local_api_url = f"http://localhost:3000/search?firstName={player['firstName']}&lastName={player['lastName']}&birthDate={player['birthDate']}&fullName={player['playerName']}"
    query = gql(
        """
        query($birthDate: Date!) {
            allPlayersByBirthDate(
                
                birthDate: $birthDate
                ) {
                    mlbId
                    name
                    firstName
                    lastName
                }
        }
        """)

    variables = {
        "birthDate": player["birthDate"]
    }

    result = client.execute(query, variable_values=variables)
    all_players = result['allPlayersByBirthDate']

    if len(all_players) == 1:
        pass
    else:
        fg_player_first_name = strip_accents(player["firstName"])
        fg_player_last_name = strip_accents(player["lastName"])



        matching_player = None

        potential_matches = []
        for api_player in all_players:
            api_player_first_name = strip_accents(api_player["firstName"])
            api_player_last_name = strip_accents(api_player["lastName"])

            if fg_player_last_name == api_player_last_name or fg_player_first_name == api_player_first_name:
                potential_matches.append(api_player)

            if len(potential_matches) == 1:
                matching_player = potential_matches[0]
                break
            elif len(potential_matches) > 1:
                print(
                    f"could not match player(s) with birth date {player['birthDate']}. possible matches:")
                for api_player in all_players:
                    print(f"{api_player['name']}")

        if not matching_player:
            print('match failed: ' + player['playerName'])
        else:
            update_mutation = gql(
                """
                
                mutation(
                    $mlbId: String,
                    $fangraphsMinorMasterId: String,
                    $fangraphsOrgProspectRanking: Int,
                    $fangraphsOverallProspectRanking: Int
                    ) {
                    updatePlayerByMlbId(
                        mlbId: $mlbId
                        fangraphsMinorMasterId: $fangraphsMinorMasterId
                        fangraphsOrgProspectRanking: $fangraphsOrgProspectRanking
                        fangraphsOverallProspectRanking: $fangraphsOverallProspectRanking
                    ) {
                        mlbId
                    }
                }""")

            variables = {
                "mlbId": matching_player["mlbId"],
                "fangraphsMinorMasterId": player["minorMasterId"],
                "fangraphsOrgProspectRanking": player["orgRank"],
                "fangraphsOverallProspectRanking": player["ovrRank"]
            }

            result = client.execute(update_mutation, variable_values=variables)

    # result = client.execute(query, variable_values={
    #     "name": strip_accents(player["playerName"]),
    #     "birthDate": player["birthDate"],
    # })

    # if (len(result["playersByNameAndBirthDate"]) == 0):
    #     result = client.execute(query, variable_values={
    #         "name": player["playerName"],
    #         "birthDate": player["birthDate"],
    #     })
    #     if len(result["playersByNameAndBirthDate"]) == 0:
    #         print(f"{player['playerName']} not found")
    #         continue

    # if len(result['playersByNameAndBirthDate']) == 0:
    #     print(f"{player['playerName']} not found")
    #     continue

    # # print(local_api_url)
    # response = requests.get(local_api_url)
    # code = response.status_code
    # if code == 400:
    #     raise Exception(f"{local_api_url} returned {code}")
    # data = response.json()

    # if len(data) == 0:
    #     print("No player found for {}".format(player['playerName']))
    #     continue
