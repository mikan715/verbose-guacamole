# main.py

from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient, errors
from bson.json_util import dumps
import os
import re

app = Flask(__name__)

uri = "mongodb+srv://hallominkenberg:x70c0y5QHod1DkX4@cluster0.3pvrh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# MongoDB-Konfiguration
#MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_URI = "mongodb+srv://hallominkenberg:x70c0y5QHod1DkX4@cluster0.3pvrh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = 'football_db'
COLLECTION_FIXTURES = 'fixtures'
COLLECTION_USERS = 'users'
COLLECTION_BETLOGS = 'betlogs'
COLLECTION_FIXTUREDFB = 'fixtureDFB'
COLLECTION_FIXTUREBL = 'fixtureBL'


# MongoDB-Client initialisieren
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection_fixtures = db[COLLECTION_FIXTURES]
collection_users = db[COLLECTION_USERS]
collection_betlogs = db[COLLECTION_BETLOGS]
collection_fixturesDFB = db[COLLECTION_FIXTUREDFB]
collection_fixturesBL = db[COLLECTION_FIXTUREBL]

def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Testen der Verbindung durch Abrufen der Serverinformationen
        client.server_info()  # Dies löst eine Exception aus, wenn keine Verbindung besteht
        return client
    except errors.ServerSelectionTimeoutError as err:
        print(f"MongoDB-Verbindung fehlgeschlagen: {err}")
        return None
    

def fetch_all_pages(url, headers):
    all_responses = []
    current_page = 1
    total_pages = 1

    while current_page <= total_pages:
        response = requests.get(f"{url}&page={current_page}", headers=headers)
        response.raise_for_status()
        data = response.json()

        # Fügen Sie nur die Einträge unter 'response' hinzu
        all_responses.extend(data.get('response', []))

        # Paging-Informationen aktualisieren
        current_page = data['paging']['current'] + 1
        total_pages = data['paging']['total']

    return all_responses


@app.route('/', methods=['GET'])
def get_data_from_db():
    try:
        # Abrufen aller Dokumente aus der Collection
        data = list(collection_fixturesBL.find())
        user = list(collection_users.find())
        print(user)

        # Extraktion und Sortierung der Daten basierend auf der Zahl im Feld "league.round"
        def extract_number(round_string):
            # Verwende reguläre Ausdrücke, um die Zahl am Ende des Strings zu extrahieren
            match = re.search(r'Regular Season - (\d+)', round_string)
            return int(match.group(1)) if match else 0

        # Sortieren der Daten basierend auf der extrahierten Zahl
        sorted_data = sorted(data, key=lambda x: extract_number(x.get('league', {}).get('round', 'Regular Season - 0')))

        # Konvertieren der Dokumente in JSON
        data_json = dumps(sorted_data)

        return data_json, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/fetch-and-store-data', methods=['GET'])
def fetch_combine_store_data():
    try:
        # URLs und Header konfigurieren
        fixtures = 'https://v3.football.api-sports.io/fixtures?league=78&season=2024'
        #fixtures = 'https://v3.football.api-sports.io/fixtures?league=81&season=2024'
        bets = 'https://v3.football.api-sports.io/odds?league=78&season=2024&bookmaker=27&bet=1'
        #bets = 'https://v3.football.api-sports.io/odds?league=81&season=2024&bookmaker=22&bet=1'
        headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': "b65e03f57a3fef50c43dfbff73e002e1"
        }

        response1 = requests.get(fixtures, headers=headers)
        response1.raise_for_status()
        all_fixtures = response1.json()['response']
        #print('all fixtures', all_fixtures)

        all_odds = fetch_all_pages(bets, headers)
        #print('all odds', all_odds)

        combined_data = []
        for fixture in all_fixtures:
            fixture_id = fixture['fixture']['id']
            print('fixture id', fixture_id)

            # Suchen der passenden Odds für das Fixture
            matching_odds = next((item for item in all_odds if item['fixture']['id'] == fixture_id), None)
            print('matiching odds', matching_odds)

            cleaned_fixture = {
                "league": fixture.get("league", {}),
                "fixture": fixture.get("fixture", {}),
                "teams": fixture.get("teams", {}),
                "goals": fixture.get("goals", {}),
                "score": fixture.get("score", {}),
                "update": fixture.get("update", ""),
                "bookmakers": matching_odds['bookmakers'] if matching_odds else []
            }
            #print(cleaned_fixture)
            combined_data.append(cleaned_fixture)

        # Vor dem Speichern alle Einträge in der Collection löschen
        collection_fixturesBL.delete_many({})

        # Neue Daten in MongoDB speichern
        if combined_data:
            collection_fixturesBL.insert_many(combined_data)
            return jsonify({"message": "Daten erfolgreich abgerufen, alte Einträge gelöscht und neue gespeichert!"}), 200
        else:
            return jsonify({"message": "Keine Daten zum Speichern."}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/addnewuser', methods=['POST'])
def create_user():
    data = request.json
    user = {
        'name': data.get('name'),
        'balance': data.get('balance', 0.0)  # Startkontostand
    }
    user_id = collection_users.insert_one(user).inserted_id
    return jsonify({'user_id': str(user_id)}), 201


if __name__ == '__main__':
    app.run(debug=True)