import requests
import json

url = "https://api.ftcscout.org/graphql"

query = """
query {
  eventByCode(code: "USCANOEBM1", season: 2025) {
    matches {
      matchNum
      teams {
        teamNumber
        alliance
        surrogate
      }
    }
  }
}
"""

print("Checking Surrogate Field...")
try:
    response = requests.post(url, json={'query': query})
    if "Cannot query field" in response.text:
       print("surrogate field DOES NOT EXIST on MatchTeam")
    else:
       print("surrogate field EXISTS")
       print(json.dumps(response.json(), indent=2)[:500])
except Exception as e:
    print(e)
