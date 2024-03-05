import pathlib
import re
import random
import json

from dotenv import dotenv_values

import requests

from flask import Flask, render_template, url_for, g
from flask_socketio import SocketIO
from datetime import datetime

# My additional functionality
from text_classification import classify
from plot_g_html import plot_diagram
from ml_predictions import predict_by_linear_regression


# Need for prompt
TIKTOK_REGEX = r'https?:\/\/(?:www\.)?tiktok\.com\/(?:@[\w.]+(?:\/video\/\d+)?|music\/[\w-]+-\d+)\s?'

PARENT_DIR = pathlib.Path(__file__).parent.resolve()

app = Flask(__name__, template_folder=PARENT_DIR / 'templates', static_folder=PARENT_DIR / 'static')
app.config['SECRET_KEY'] = "asi4rjkl"

socketio = SocketIO(app)
config = dotenv_values('.env')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('user_prompt')
def on_user_prompt(prompt):
    match classify(prompt):
        case label, answer:
            # Little a bit debugging
            print(label)

            answer_data = {
                'user_prompt': prompt,
                'copilot_answer': answer
            }

            # Copilot answer with graphs only when link for TikTok sound or account or video is provided
            if link := re.findall(TIKTOK_REGEX, prompt):
                if label == 1:
                    graph_url = request_account_analytic(link[0])
                    answer_data |= {'graphs': graph_url}
                elif label == 2:
                    graph_url = request_song_analytic(link[0])
                    answer_data |= {'graphs': graph_url}
                else:
                    graph_url = request_prediction_popularity_by_song(link[0])
                    answer_data |= {'graphs': graph_url}
            else:
                socketio.emit('copilot_answer', answer_data.update(
                    {'copilot_answer': 'Please provide me a link'}))

            # More debugging
            print(answer_data)
            socketio.emit('copilot_answer', answer_data)
        case _:
            print("There is error")


def _get_headers_for_flai_request() -> dict:
    headers = {
        'Accept': 'application/json',
        'Token': config['FLAI_TOKEN']
    }

    return headers


# Function that recursively gets all keys in dict
def get_keys(dct: dict) -> set:
    keys = set()
    if isinstance(dct, dict):
        for key, value in dct.items():
            keys.add(key)
            keys.update(get_keys(value))
    elif isinstance(dct, list):
        for item in dct:
            keys.update(get_keys(item))
    return keys


def get_random_tt_account_id() -> int:
    endpoint = "https://flaidata.tiktok-alltrends.com:442/api/datapoint/authors?take=10&Verified=unverified&SubscribersTo=10000&SubscribersFrom=1000&ClipsTo=5000&ClipsFrom=1000&VideosLocation=GB&ArtistLocation=GB&Sorting=subs&Order=desc"
    random_accounts = requests.get(endpoint, headers=_get_headers_for_flai_request())
    accounts_id = [stat['authorId'] for stat in random_accounts.json()['data']['stats']]
    return int(random.choice(accounts_id))


def get_random_tt_sound_info() -> dict:
    endpoint = "https://flaidata.tiktok-alltrends.com:442/api/datapoint/sounds?sorting=rate&take=3&soundType=Original&Days=7&VideosLocation=US&Category=95"
    sounds = requests.get(endpoint, headers=_get_headers_for_flai_request())
    random_sound_data = random.choice([stat['music'] for stat in sounds.json()['data']['stats']])
    return random_sound_data


def get_random_tt_sound_extended() -> dict:
    endpoint = 'https://flaidata.tiktok-alltrends.com:442/api/datapoint/soundsextended?sorting=rise&take=10&soundType=Original&Days=3&VideosLocation=US&Category=95'
    sounds_extended = requests.get(endpoint, headers=_get_headers_for_flai_request())
    print(sounds_extended)
    random_sound_data = random.choice(sounds_extended.json()['data']['stats'])
    return random_sound_data


def get_author_data(author_id: int) -> dict:
    endpoint = "https://flaidata.tiktok-alltrends.com:442/api/datapoint/author"

    params = {
        'authorId': author_id,
        'period': 7
    }

    account_data = requests.get(endpoint, headers=_get_headers_for_flai_request(), params=params)
    return account_data.json()


def _write_json_local(json_obj, title):
    with open(title + '.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_obj))


# ARGUMENT IS NOT USED because the api hasn't been finalized yet.
# Called when user requested analytic for account
def request_account_analytic(account_link: str) -> list:
    print("GETTING ACCOUNT FROM API")
    random_account_id = get_random_tt_account_id()
    account_data = get_author_data(random_account_id)

    # ---------- If there is no response from above uncomment below --------
    # _write_json_local(account_data['calculations'], 'calculations')

    # with open('calculations.json', 'r') as json_file:
    #     account_data = json.load(json_file)

    account_data = account_data['calculations']
    values = list(account_data.values())
    names = list(account_data.keys())
    filename = plot_diagram(values=values,
                            names=names,
                            title=f'Analytic of account {account_data["authorId"]}',
                            exclude=['authorId'],
                            chart_type='pie')

    return [url_for('static', filename=filename)]


# Called when user requested analytic for song
def request_song_analytic(song_or_video_link: str) -> list:
    print("GETTING SOUND FROM API")
    sound = get_random_tt_sound_extended()
    # sound = get_random_tt_sound_info()  # not response
    # ------------- If there is no response from api uncomment lines below ------
    # sound = {
    #     "music": {
    #         "musicId": "7184117852214692613",
    #         "reposts": 21900,
    #         "duration": 45,
    #         "album": "",
    #         "url": "https://v77.tiktokcdn.com/2caacbb426ddff896eb676c6a2e46fd5/65004737/video/tos/useast2a/tos-useast2a-v-27dcd7/owbHSLAdjSBcEfPzBYeDQ0nnUsCJ5y8UI0btJx/?a=1233&ch=0&cr=0&dr=0&er=2&cd=0%7C0%7C0%7C0&br=250&bt=125&bti=NDU3ZjAwOg%3D%3D&ft=d2A~l-Inz7TSFKmZiyq8Z&mime_type=audio_mpeg&qs=6&rc=OjloOGhoNjQ5Ojg1ZzNlZ0Bpanl5NmY6ZjxraDMzNzU8M0BiMzUwNDU2Ni0xLzY0NF5iYSNiYWBhcjRvbm1gLS1kMTZzcw%3D%3D&l=202309121010009E90E7C4AB678D029470&btag=e00088000&cc=13&download=true",
    #         "title": "الصوت الأصلي",
    #         "creator": "ياسر عبد الوهاب",
    #         "musicOriginal": True,
    #         "parseDate": "2023-09-11T15:22:25.892215",
    #         "updateDate": "2023-09-12T10:10:26.312805",
    #         "parser": "SoundItem",
    #         "dailyRise": 100,
    #         "artistRegion": "IQ"
    #     }
    # }

    values = list(sound['music'].values())
    names = list(sound['music'].keys())

    filename = plot_diagram(values=values,
                            names=names,
                            title=f'Song info {sound["music"]["musicId"]}',
                            exclude=['musicId', 'album', 'url',
                                     'title', 'creator',
                                     'musicOriginal', 'parseDate',
                                     'updateDate', 'parser',
                                     'artistRegion'],
                            chart_type='bar')

    return [url_for('static', filename=filename)]


# Adds n dates with same distance in original dates array and return only extended part
# Used in ml predicts
def extend_dates(original_dates, additional_count):
    if len(original_dates) < 2:
        raise ValueError("dates array should contains at least 2 dates")

    distance = original_dates[1] - original_dates[0]

    extended_dates = original_dates.copy()

    for _ in range(additional_count):
        new_date = extended_dates[-1] + distance
        extended_dates.append(new_date)

    return extended_dates[len(original_dates):]


# Called when user requested prediction for song or video (currently im working with song)
def request_prediction_popularity_by_song(song_or_video_link: str) -> list:
    sound = get_random_tt_sound_extended()
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    sound_video_popularity = sound['soundVideoData']
    sound_reposts_total = sound['music']['reposts']
    sound_reposts_per_day = sound['soundStates']
    daily_rise = sound['music']['dailyRise']

    # Convert parsed dates to datetime class
    datetime_dates = [datetime.strptime(elem['parseDate'], date_format) for elem in sound_reposts_per_day]
    # Take amount of reposts
    sound_reposts = [elem['reposts'] for elem in sound_reposts_per_day]
    # Extend original dates for ML
    extended_dates = extend_dates(datetime_dates, len(sound_reposts))

    predictions = predict_by_linear_regression(sound_reposts)

    fig1 = plot_diagram(names=datetime_dates,
                        values=sound_reposts,
                        additional_names=extended_dates,
                        ml_predicted_values=predictions.squeeze().tolist(),
                        title='Reposts and prediction',
                        chart_type='line')

    fig2 = plot_diagram(names=list(sound_video_popularity.keys()),
                        values=list(sound_video_popularity.values()),
                        title='Video popularity',
                        chart_type='pie')

    fig3 = plot_diagram(names=['daily rise', 'total reposts'],
                        values=[daily_rise, sound_reposts_total],
                        title='Song statistic',
                        chart_type='bar')

    return [url_for('static', filename=fig) for fig in (fig1, fig2, fig3)]


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
