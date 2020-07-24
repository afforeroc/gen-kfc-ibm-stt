#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obtain transcripts of various audio files using 'IBM STT' service."""

import os
import json
from dotenv import load_dotenv
import pandas as pd
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class MyRecognizeCallback(RecognizeCallback):
    """Class provided by IBM."""
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        #print(json.dumps(data, indent=2))
        with open('json/ws_sample.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
        print("'json/ws_sample.json' was saved sucessful")

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))


def load_env(env_file):
    """Load authentication settings for SST service."""
    dotenv_path = os.path.join(os.path.dirname(__file__), env_file)
    load_dotenv(dotenv_path)
    api_key = os.getenv('API_KEY')
    url_service = os.getenv('API_URL')
    return api_key, url_service


def instantiate_stt(api_key, url_service):
    """Link a SDK instance with a IBM STT instance."""
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url_service)
    return speech_to_text


def extract_keywords(excel_pathfile, header):
    """Extract 'keywords' from excel file and return it as a list."""
    data_frame = pd.read_excel(excel_pathfile, header=header)
    keyword = data_frame.iloc[:, 0].values.tolist()
    return keyword


def print_json(data_json):
    """Print in console a JSON data in beautiful style."""
    json_data = json.dumps(data_json, indent=2,
                           ensure_ascii=False).encode('utf32')
    print(json_data.decode())


def save_json(data_json, audio_file, transcripts_folder):
    """Save a successful callback on a JSON file."""
    name_file = os.path.splitext(audio_file)[0]
    json_pathfile = f'{transcripts_folder}/{name_file}.json'
    with open(json_pathfile, 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, indent=2, ensure_ascii=False)
    print(f"'{json_pathfile}' was saved sucessful")


def sst_response(audio_pathfile, speech_to_text, keywords):
    """Return callback response of SST using one audiofile."""
    my_recognize_callback = MyRecognizeCallback()
    with open((audio_pathfile), 'rb') as audio_file:
        audio_source = AudioSource(audio_file)
        speech_to_text.recognize_using_websocket(
            audio=audio_source,
            content_type='audio/mp3',
            recognize_callback=my_recognize_callback,
            model='es-CO_NarrowbandModel',
            keywords=keywords,
            keywords_threshold=0.5,
            speaker_labels=True)


def main():
    """Load audios, make transcripts using 'IBM SST' service and after save them in JSON folder."""
    api_key, url_service = load_env('.env')
    speech_to_text = instantiate_stt(api_key, url_service)
    keywords = extract_keywords("basekeywords_db.xlsx", 0)

    audios_folder = "audios"
    for audio_file in os.listdir(audios_folder):
        audio_pathfile = os.path.join(audios_folder, audio_file)
        print(audio_pathfile)
        if os.path.isfile(audio_pathfile):
            sst_response(audio_pathfile, speech_to_text, keywords)


if __name__ == '__main__':
    main()
