#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Obtain transcripts of various audio files using 'IBM STT' service."""

import os
import json
from dotenv import load_dotenv
import re
import unicodedata
import pandas as pd
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def load_env():
    """Load authentication settings for SST service."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    api_key = os.getenv('API_KEY')
    url_service = os.getenv('URL_SERVICE')
    return api_key, url_service

def strip_accents(text):
    """Quit accent of vowels."""
    try:
        text = unicode(text, 'utf-8')
    except NameError:  # unicode is a default on python 3
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii',
                                                     'ignore').decode("utf-8")
    return str(text)


def extract_keywords(excel_pathfile, columns):
    """Extract all keywords in lowercase, without: accents, special characters, extra spaces."""
    data_frame = pd.read_excel(excel_pathfile)
    keyword_list = []
    for i in range(columns):
        keyword_list += data_frame.iloc[:, i].dropna().values.tolist()
    keywords_set = set()
    for i, keyword in enumerate(keyword_list):
        keyword = str(keyword)
        if keyword != '':
            keyword = keyword.lower().replace('ñ', 'yn')
            keyword = strip_accents(keyword)
            keyword = re.sub(r"[^a-zA-Z0-9]+", ' ', keyword).strip()
            keyword = keyword.lower().replace('yn', 'ñ')
            keywords_set.add(keyword)
    return list(keywords_set)


def print_json(data_json):
    """Print in console a JSON data in beautiful style."""
    json_data = json.dumps(data_json, indent=2,
                           ensure_ascii=False).encode('utf8')
    print(json_data.decode())


def save_json(data_json, audio_file, transcripts_folder):
    """Save a successful callback on a JSON file."""
    name_file = os.path.splitext(audio_file)[0]
    json_pathfile = f'{transcripts_folder}/{name_file}.json'
    with open(json_pathfile, 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, indent=2, ensure_ascii=False)
    print(f"'{json_pathfile}' was saved sucessful")


def sst_response(audio_pathfile, speech_to_text, keywords_list):
    """Return callback response of SST using one audiofile."""
    with open((audio_pathfile), 'rb') as audio_file:
        response = speech_to_text.recognize(audio=audio_file,
                                            content_type='audio/mp3',
                                            model='es-CO_NarrowbandModel',
                                            keywords=keywords_list,
                                            keywords_threshold=0.5,
                                            speaker_labels=True).get_result()
    return response


def main():
    """Load audios, make transcripts using 'IBM SST' service and after save them in JSON folder."""
    api_key, url_service = load_env()
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url_service)

    keywords_list = extract_keywords('keywords_revised.xlsx', 1)
    print(keywords_list)

    audios_folder = "audios"
    transcripts_folder = "transcripts"
    for audio_file in os.listdir(audios_folder):
        audio_pathfile = os.path.join(audios_folder, audio_file)
        if os.path.isfile(audio_pathfile):
            data_json = sst_response(audio_pathfile, speech_to_text, keywords_list)
            save_json(data_json, audio_file, transcripts_folder)


if __name__ == '__main__':
    main()
