from bson import ObjectId
from bson.json_util import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import time
import requests
import re
import os
import sys
import logging
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import atexit

app = Flask(__name__)
CORS(app)
load_dotenv()

rapidapi_host = os.getenv('RAPIDAPI_HOST')
rapidapi_key = os.getenv('RAPIDAPI_KEY')

MONGO_URI = os.getenv('MONGO_URI')
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

shared_data_frontend = {
    "username": "Anne"
}

def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Testen der Verbindung durch Abrufen der Serverinformationen
        client.server_info()  # Dies löst eine Exception aus, wenn keine Verbindung besteht
        print(client)
        return client
    except errors.ServerSelectionTimeoutError as err:
        print(f"MongoDB-Verbindung fehlgeschlagen: {err}")
        return None

@app.route('/login', methods=['GET'])
def search():
    # Suche nach einem Parameter in der URL
    username = request.args.get('username')
    print(username)
    
    if not username:
        return jsonify({'error': 'Username parameter is required'}), 400

    # Suche nach dem Benutzer in der MongoDB
    user_data = collection_users.find_one({'name': username})
    print(user_data)
    
    if user_data:
        """ shared_data_frontend["username"] = username """
        user_data['_id'] = str(user_data['_id'])
        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/dashboard', methods=['GET'])
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

        # Extraktion des Datums aus fixture.date
        def parse_date(date_string):
            # Wandelt das Datum in ein datetime-Objekt um
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))

        # Sortieren der Daten zuerst nach der extrahierten Zahl und dann nach dem Datum
        sorted_data = sorted(data, key=lambda x: (
            extract_number(x.get('league', {}).get('round', 'Regular Season - 0')),
            parse_date(x.get('fixture', {}).get('date', '1970-01-01T00:00:00+00:00'))
        ))

        # Konvertieren der Dokumente in JSON
        data_json = dumps(sorted_data)

        return data_json, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/addnewuser', methods=['POST'])
def create_user():
    data = request.json
    user = {
        'name': data.get('name'),
        'balance': data.get('balance', 0.0),
        'bets': data.get('bets', []),
    }
    user_id = collection_users.insert_one(user).inserted_id
    return jsonify({'user_id': str(user_id)}), 201

@app.route('/add_bet', methods=['POST'])
def add_bet():
    # Daten von der Anfrage abrufen
    user_id = request.json.get('user_id')
    fixture = request.json.get('fixture')
    wettgeld = request.json.get('wettgeld')
    odd = request.json.get('odd')
    value = request.json.get('value')

    print(user_id)
    print(fixture)
    print(wettgeld)
    print(odd)
    print(value)

    # Überprüfen, ob alle Felder vorhanden sind
    """ if not user_id or not fixture or not wettgeld or not odd or not value:
        return jsonify({'error': 'All fields (user_id, game, amount, odds) are required'}), 400 """

    # Den Benutzer in der Datenbank finden
    user = collection_users.find_one({'name': user_id})
    print(user)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Neue Wette erstellen
    new_bet = {
        'fixture': fixture,
        'wettgeld': wettgeld,
        'odd': odd,
        'value': value,
        'checked_bet': False,
    }
    print(new_bet)

    userBalance = user.get('balance')
    new_balance = float(userBalance) - float(wettgeld)

    # Wetten-Array aktualisieren
    collection_users.update_one({'name': user_id}, {'$push': {'bets': new_bet}, '$set': {'balance': new_balance}})

    return jsonify({'message': 'Bet added successfully'}), 200

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

def fetch_combine_store_data():
    current_time = datetime.utcnow()
    print("fetch new data", current_time)
    
    # First, check if we need to update the data
    latest_record = collection_fixturesBL.find_one(
        {},
        sort=[('fixture.update', -1)]
    )
    
    # Only update if no data exists or data is older than 1 hour
    if latest_record:
        last_update = latest_record['fixture'].get('update')
        if last_update and (current_time - datetime.fromisoformat(last_update)) < timedelta(hours=0.1):
            return jsonify({"message": "Using existing data (less than 1 hour old)"}), 200

    try:
        headers = {
            'x-rapidapi-host': rapidapi_host,
            'x-rapidapi-key': rapidapi_key
        }

        # Make a single call for fixtures with odds included
        fixtures_url = 'https://v3.football.api-sports.io/fixtures?league=78&season=2024&odds=27'
        all_data = fetch_all_pages(fixtures_url, headers)

        if not all_data:
            return jsonify({"message": "No data received from API"}), 200

        # Process and clean the data
        combined_data = [{
            "league": item.get("league", {}),
            "fixture": item.get("fixture", {}),
            "teams": item.get("teams", {}),
            "goals": item.get("goals", {}),
            "score": item.get("score", {}),
            "update": item.get("update", ""),
            "bookmakers": item.get("odds", [])
        } for item in all_data]

        # Update MongoDB
        collection_fixturesBL.delete_many({})
        if combined_data:
            collection_fixturesBL.insert_many(combined_data)
            return jsonify({"message": "Data successfully updated!"}), 200
        
        return jsonify({"message": "No data to store."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def check_bet():
    print("--- check bets ---")
    current_time = datetime.utcnow()  # Get current UTC time
    user = collection_users.find_one({"name": shared_data_frontend.get("username")})
    userBalance = user.get('balance')
    if not user:
        print("User not found")
        return
    
    for bet in user.get('bets', []):
        fixture_id = bet.get('fixture')
        wettgeld = bet.get('wettgeld')
        oddTeam = bet.get('odd')
        oddValue = bet.get('value')
        checked_bet = bet.get('checked_bet')
        fixture = collection_fixturesBL.find_one({
            "fixture.id": fixture_id,
            "fixture.status.short": "FT"
        })

        print('--- start ---')
        print('oddTeam', oddTeam)
        print('checked_bet', checked_bet)

        if checked_bet == True:
            print('bet already checked')
            collection_users.update_one(
                {"name": shared_data_frontend.get("username"), "bets.fixture": fixture_id},
                {"$set": {
                    "bets.$.last_check": current_time,
                }}
            )
        elif fixture:
            winner_home = fixture.get('teams', {}).get('home', {}).get('winner')
            winner_away = fixture.get('teams', {}).get('away', {}).get('winner')

            print('winner home', winner_home)
            print('winner away', winner_away)

            if winner_home == True and oddTeam == "Home":
                countOdd(wettgeld, oddValue, fixture_id, userBalance, current_time)
                print('wette gewonnen home')
            elif winner_away == True and oddTeam == "Away":
                countOdd(wettgeld, oddValue, fixture_id, userBalance, current_time)
                print('wette gewonnen away')
            elif winner_home != True and winner_away != True and oddTeam == "Draw" :
                countOdd(wettgeld, oddValue, fixture_id, userBalance, current_time)
                print('wette gewonnen draw')
            else:
                # Only update checked_bet and result_time for completed bets
                collection_users.update_one(
                    {"name": shared_data_frontend.get("username"), "bets.fixture": fixture_id},
                    {"$set": {
                        "bets.$.checked_bet": True,
                        "bets.$.result_time": current_time,
                        "bets.$.last_check": current_time,
                    }}
                )
                print('wette nicht gewonnen')

            print('--- end ---')
        else:
            collection_users.update_one(
                {"name": shared_data_frontend.get("username"), "bets.fixture": fixture_id},
                {"$set": {
                    "bets.$.last_check": current_time,
                }}
            )
            print(f"No fixture found {fixture}")
        
def countOdd(wettgeld, oddValue, fixture, userBalance, check_time):
    win_amount = float(wettgeld) * float(oddValue)
    new_balance = userBalance + win_amount
    collection_users.update_one(
        {"name": shared_data_frontend.get("username"), "bets.fixture": fixture},
        {
            "$set": {
                "bets.$.checked_bet": True,
                "bets.$.result_time": check_time,  # When the bet was determined won/lost
                "bets.$.last_check": check_time,
                "balance": new_balance
            }
        }
    )
    print(f"User won the bet. New balance: {new_balance}")
    return new_balance


def start_scheduler():
    print("Starting scheduler...")
    scheduler = BackgroundScheduler(daemon=True)
    
    # Existing job for checking bets
    scheduler.add_job(
        func=check_bet,
        trigger="interval",
        minutes=3,
        id="check_bet_job",
        name="Check bets every minute",
        replace_existing=True,
        misfire_grace_time=None
    )
    
    # New job for fetching data
    scheduler.add_job(
        func=fetch_combine_store_data,
        trigger="interval",
        minutes=15,
        id="fetch_data_job",
        name="Fetch data every 15 minutes",
        replace_existing=True,
        misfire_grace_time=None
    )
    
    scheduler.start()
    
    jobs = scheduler.get_jobs()
    
    atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fetch_data':
        print("hell yes, i'm Running fetch_data job")
        fetch_combine_store_data()
    else:
        try:
            start_scheduler()
            app.run(debug=False, host='0.0.0.0', port=int(os.getenv("PORT", 8000)))
        except Exception as e:
            raise

