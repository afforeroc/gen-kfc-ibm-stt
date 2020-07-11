#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert a series of audio files to text using IBM Speech To Text service."""

import os
import json
from dotenv import load_dotenv
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def load_env():
    """ Load auth elements for SST service."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    api_key = os.getenv('API_KEY')
    url_service = os.getenv('URL_SERVICE')
    return api_key, url_service


def print_json(data):
    """Print in console a JSON data in beautiful style."""
    json_data = json.dumps(data, indent=2, ensure_ascii=False).encode('utf8')
    print(json_data.decode())


def save_json(data, audio_file):
    """Save a successful callback on a JSON file."""
    name_file = os.path.splitext(audio_file)[0]
    json_file_path = f'json/{name_file}.json'
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)
    print(f"'{json_file_path}' was saved sucessful")


def sst_response(audio_path, speech_to_text):
    """Return callback response of SST using one audiofile."""
    with open((audio_path), 'rb') as audio_file:
        response = speech_to_text.recognize(audio=audio_file,
                                            content_type='audio/mp3',
                                            model='es-CO_NarrowbandModel',
                                            speaker_labels=True).get_result()
    return response


def main():
    """Make multiple SST callbacks. After, receive and save the SST responses on JSON files."""
    api_key, url_service = load_env()
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url_service)

    audios_folder = "audios"
    for audio_file in os.listdir(audios_folder):
        audio_file_path = os.path.join(audios_folder, audio_file)
        if os.path.isfile(audio_file_path):
            data = sst_response(audio_file_path, speech_to_text)
            save_json(data, audio_file)


if __name__ == '__main__':
    main()
