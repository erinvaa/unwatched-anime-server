import requests
from datetime import datetime, timedelta
import json
from flask import Flask, request

app = Flask(__name__)


# CONSTANTS - TODO reorganize and rename
aired_episodes_key = 'anime_aired_episodes' # My own creation

anime_airing_status_key = 'anime_airing_status'
anime_num_episodes_key = 'anime_num_episodes'
anime_start_date_key = 'anime_start_date_string'
anime_id_key = 'anime_id'

senpai_api_url = 'http://www.senpai.moe/export.php?type=json&src=raw'

mal_id_key = 'MALID'
air_date_key = 'airdate_u'


start_time_map = {}


@app.before_first_request
def initialize():
    print("Initializing")
    load_anime_start_times()


def load_anime_start_times():
    r = requests.get(senpai_api_url)

    # TODO error handling
    if r.status_code != 200:
        pass

    data = r.json()

    for item in data['items']:
        mal_id = int(item[mal_id_key])
        air_date = item[air_date_key]
        print("Found start date for anime: " + item['name'])

        start_time_map[mal_id] = datetime.utcfromtimestamp(air_date)

    print("Loaded start times from Senpai.moe")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


# TODO remove this eventually
@app.route('/')
def root():
    return 'Root'


@app.route('/api/<string:username>/watching', methods=["GET"])
def watching(username):
    if request.method == "GET":
        mal_url_1 = 'https://myanimelist.net/animelist/'
        mal_url_2 = '/load.json?offset=0&status=1&order=1'

        print("Got request for user watching " + username)

        url = mal_url_1 + username + mal_url_2

        r = requests.get(url)

        # TODO error handling
        if r.status_code != 200:
            return 400

        data = r.json()
        add_aired_episode_count(data)

        return json.dumps(data), 200, {'ContentType': 'application/json'}


def add_aired_episode_count(data):
    current_time = datetime.utcnow()

    for anime in data:
        # Currently airing anime. Most of logic is done here.
        if anime[anime_airing_status_key] == 1:
            mal_id = anime[anime_id_key]

            print("Anime: " + str(anime['anime_title']) + " | malId: " + str(mal_id))

            start_date = start_time_map[mal_id]
            time_airing = current_time - start_date
            anime[aired_episodes_key] = int(time_airing.total_seconds() // timedelta(days=7).total_seconds() + 1)

        # Completed anime; can just assume all episodes are out
        if anime[anime_airing_status_key] == 2:
            anime[aired_episodes_key] = anime[anime_num_episodes_key]

        # Not yet airing anime; obviously nothing is out yet (probably)
        if anime[anime_airing_status_key] == 3:
            anime[aired_episodes_key] = 0