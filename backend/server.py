from flask import Flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import http.client
import json


app = Flask(__name__)

uri = "mongodb+srv://hallominkenberg:x70c0y5QHod1DkX4@cluster0.3pvrh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def getData(): 
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "b65e03f57a3fef50c43dfbff73e002e1"
    }

    # CURRENT ROUND
    currentRound = "/fixtures/rounds?league=79&season=2024&current=true"
    conn.request("GET", currentRound , headers=headers)
    res = conn.getresponse()
    data = res.read()
    current_round_data = json.loads(data.decode("utf-8"))
    current_round = current_round_data['response'][0]
    current_round = current_round.replace(" ", "%20")
    print('current round:', current_round)

    # GAMEDAY
    """ gameday = f"/fixtures?league=78&season=2023&round={current_round}"
    conn.request("GET", gameday, headers=headers)
    res = conn.getresponse()
    data = res.read()
    game_data = json.loads(data.decode("utf-8"))
    #print(data.decode("utf-8"))
 """
    # BETS
    """  bets = "/odds?league=79&season=2024&bookmaker=6&bet=1"
    conn.request("GET", bets, headers=headers)
    res = conn.getresponse()
    data = res.read()
    bets_data = json.loads(data.decode("utf-8"))
    #print(data.decode("utf-8")) """


def hauptprogramm():
    while True:
        eingabe = input("Möchtest du Daten ziehen? (ja/nein): ").lower()
        if eingabe == 'ja':
            getData()
        elif eingabe == 'nein':
            print("Die Funktion wird nicht ausgeführt.")
            break
        else:
            print("Ungültige Eingabe. Bitte antworte mit 'ja' oder 'nein'.")

if __name__ == '__main__':
    hauptprogramm()
    app.run(debug=True)
