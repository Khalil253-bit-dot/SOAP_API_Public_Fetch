
from flask import Flask, jsonify, request
from zeep import Client
from zeep.helpers import serialize_object

# --------------------------------------------------
# Connect to the FootballPool SOAP service
# --------------------------------------------------

WSDL_URL = "https://footballpool.dataaccess.eu/info.wso?WSDL"

client = Client(wsdl=WSDL_URL)

app = Flask(__name__)


# --------------------------------------------------
# Retrieve football information from SOAP
# --------------------------------------------------

def get_football_details():

    # Retrieve all players
    players = client.service.AllPlayerNames(False)

    # Retrieve player roles
    roles = client.service.PlayerRoles()

    # Retrieve all historical game results
    games = client.service.ResultsAllGames(0, 0)

    players_dict = serialize_object(players) or []
    roles_dict = serialize_object(roles) or []
    games_dict = serialize_object(games) or []

    # Return information as a Python dictionary
    return {
        "players": players_dict,
        "roles": roles_dict,
        "games": games_dict
    }

# Validation

def validate_country(country, players):

    if not isinstance(country, str) or not country.strip():
        raise ValueError("Country must be a non-empty string.")

    # Get the available country names from the player data
    valid_countries = {
        player["sCountryName"]
        for player in players
        if player.get("sCountryName")
    }

    country = country.strip()

    # Check whether the country exists
    if country not in valid_countries:

        # Check whether the problem is capitalization
        for valid_country in valid_countries:
            if country.casefold() == valid_country.casefold():
                raise ValueError(
                    f"Incorrect capitalization. Use '{valid_country}'."
                )

        raise ValueError(f"'{country}' is not a valid country.")

    return country

# GET endpoint

@app.route("/football", methods=["GET"])
def get_football():

    try:

        # Retrieve SOAP information
        football_data = get_football_details()

        # Allow an optional country filter
        country = request.args.get("country")

        if country:

            country = validate_country(country, football_data["players"])

            football_data["players"] = [
                player for player in football_data["players"]
                if player["sCountryName"] == country
            ]

        return jsonify(football_data), 200

    except ValueError as exc:
        return jsonify({
            "error": f"Invalid input. Something went wrong: {exc}"
        }), 400

    except Exception as exc:
        return jsonify({
            "error": f"Something went wrong: {exc}"
        }), 502

# POST endpoint

@app.route("/football", methods=["POST"])
def post_football():

    try:

        # Receive JSON information from the user
        user_data = request.get_json(silent=True)

        if not isinstance(user_data, dict):
            raise ValueError("Request must contain valid JSON.")

        if "country" not in user_data:
            raise ValueError("Please provide a country.")

        # Retrieve SOAP information
        football_data = get_football_details()

        # Validate the country supplied by the user
        country = validate_country(user_data["country"], football_data["players"])

        # Filter players by the selected country
        football_data["players"] = [
            player for player in football_data["players"]
            if player["sCountryName"] == country
        ]

        # Return the filtered information
        return jsonify(football_data), 200

    except ValueError as exc:
        return jsonify({
            "error": f"Invalid input. Something went wrong: {exc}"
        }), 400

    except Exception as exc:
        return jsonify({
            "error": f"Something went wrong: {exc}"
        }), 502


if __name__ == "__main__":
    app.run(debug=True)
