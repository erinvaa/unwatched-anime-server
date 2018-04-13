import requests
from datetime import datetime, timedelta
import json
from flask import Flask, request
from database import db, VideoSource, VideoSourceType, SkippedEpisodes, CustomVideoSource, User

DB_PATH = "database.db"
SQL_PREFIX = 'sqlite:///'


class Config(object):
    SQLALCHEMY_DATABASE_URI = SQL_PREFIX + DB_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


# CONSTANTS - TODO reorganize and rename
AIRED_EPISODES_KEY = 'anime_aired_episodes'  # My own creation
SOURCES_KEY = 'sources'

ANIME_AIRING_STATUS_KEY = 'anime_airing_status'
ANIME_NUM_EPISODES_KEY = 'anime_num_episodes'
ANIME_START_DATE_KEY = 'anime_start_date_string'
ANIME_ID_KEY = 'anime_id'

SENPAI_API_URL = 'http://www.senpai.moe/export.php?type=json&src=raw'

MAL_ID_KEY = 'MALID'
AIR_DATE_KEY = 'airdate_u'


start_time_map = {}


@app.before_first_request
def initialize():
    print("Initializing")
    load_anime_start_times()


def load_anime_start_times():
    r = requests.get(SENPAI_API_URL)

    # TODO error handling
    if r.status_code != 200:
        pass

    data = r.json()

    for item in data['items']:
        mal_id = int(item[MAL_ID_KEY])
        air_date = item[AIR_DATE_KEY]
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
        user = User.query.filter_by(mal_name=username).first()
        add_aired_episode_count(data)
        add_video_source(data, user)

        return json.dumps(data), 200, {'ContentType': 'application/json', "Access-Control-Allow-Origin": '*'}


@app.route('/api/video-sources', methods=["GET"])
def sources():
    if request.method == "GET":
        types = VideoSourceType.query.all()

        retval = {}

        for host_type in types:
            retval[host_type.id] = {
                "name": host_type.name,
                "icon_url": host_type.icon_url
            }

        return json.dumps(retval), 200, {'ContentType': 'application/json', "Access-Control-Allow-Origin": '*'}


def add_video_source(data, user):
    for anime in data:
        mal_id = anime[ANIME_ID_KEY]
        sources = {}

        video_sources = VideoSource.query.filter_by(mal_id=mal_id).all()

        for source in video_sources:
            sources[source.type.id] = source.url

        custom_video_sources = CustomVideoSource.query.filter_by(mal_id=mal_id, user=user).all()

        for source in custom_video_sources:
            sources[source.type.id] = source.url

        anime[SOURCES_KEY] = sources


def add_aired_episode_count(data):
    current_time = datetime.utcnow()

    for anime in data:
        # Currently airing anime. Most of logic is done here.
        if anime[ANIME_AIRING_STATUS_KEY] == 1:
            mal_id = anime[ANIME_ID_KEY]

            print("Anime: " + str(anime['anime_title']) + " | malId: " + str(mal_id))

            start_date = start_time_map[mal_id]
            time_airing = current_time - start_date

            skipped_episodes = get_skipped_episodes(mal_id)

            anime[AIRED_EPISODES_KEY] = int(time_airing.total_seconds() // timedelta(days=7).total_seconds()
                                            + 1 - skipped_episodes)

        # Completed anime; can just assume all episodes are out
        if anime[ANIME_AIRING_STATUS_KEY] == 2:
            anime[AIRED_EPISODES_KEY] = anime[ANIME_NUM_EPISODES_KEY]

        # Not yet airing anime; obviously nothing is out yet (probably)
        if anime[ANIME_AIRING_STATUS_KEY] == 3:
            anime[AIRED_EPISODES_KEY] = 0


def get_skipped_episodes(mal_id):
    skipped_episodes_obj = SkippedEpisodes.query.filter_by(mal_id=mal_id).first()
    if skipped_episodes_obj is None:
        return 0
    else:
        return skipped_episodes_obj.skipped_episodes
