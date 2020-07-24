#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obtain JSON responses from 'IBM SST' audio processing."""

import os
import json
from dotenv import load_dotenv
import pandas as pd
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def load_env(env_file):
    """Load authentication settings of a IBM STT instance."""
    dotenv_path = os.path.join(os.path.dirname(__file__), env_file)
    load_dotenv(dotenv_path)
    api_key = os.getenv('API_KEY')
    url_service = os.getenv('API_URL')
    return api_key, url_service


def instantiate_stt(api_key, url_service):
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url_service)
    return speech_to_text


def extract_keywords(excel_pathfile, header):
    """Extract 'keywords' from excel file and return it as a list."""
    data_frame = pd.read_excel(excel_pathfile, header=header)
    keyword_list = data_frame.iloc[:, 0].values.tolist()
    return keyword_list


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
    with open((audio_pathfile), 'rb') as audio_file:
        response = speech_to_text.recognize(audio=audio_file,
                                            content_type='audio/mp3',
                                            model='es-CO_NarrowbandModel',
                                            keywords=keywords,
                                            keywords_threshold=0.5,
                                            speaker_labels=True).get_result()
    return response


def main():
    """Obtain JSON responses from 'IBM SST' audio processing."""
    api_key, url_service = load_env('.env')
    speech_to_text = instantiate_stt(api_key, url_service)
    keywords = extract_keywords("basekeywords_db.xlsx", 0)
    audios_folder = "audios"
    json_folder = "json"
    for audio_file in os.listdir(audios_folder):
        audio_pathfile = os.path.join(audios_folder, audio_file)
        if os.path.isfile(audio_pathfile):
            data_json = sst_response(audio_pathfile, speech_to_text, keywords)
            save_json(data_json, audio_file, json_folder)


if __name__ == '__main__':
    main()
