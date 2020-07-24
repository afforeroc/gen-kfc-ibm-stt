#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Obtain transcripts of various audio files using 'IBM STT' service."""

import os
import json
import random
import time
import re
import unicodedata
from dotenv import load_dotenv
import pandas as pd
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        #print(json.dumps(data, indent=2))
        with open('transcripts/sample.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
        print(f"'transcripts/sample.json' was saved sucessful")

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
                           ensure_ascii=False).encode('utf32')
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
    myRecognizeCallback = MyRecognizeCallback()
    with open((audio_pathfile), 'rb') as audio_file:
        audio_source = AudioSource(audio_file)
        speech_to_text.recognize_using_websocket(audio=audio_source,
                                        content_type='audio/mp3',
                                        recognize_callback=myRecognizeCallback,
                                        model='es-CO_NarrowbandModel',
                                        keywords=keywords_list,
                                        keywords_threshold=0.5,
                                        speaker_labels=True)


def obtain_bbytes(keyword_list):
    """Return the buffer size of 'keyword_list'."""
    num_nys = 0
    num_char = 0
    num_keywords = len(keyword_list)
    for kword in keyword_list:
        nys_kword = kword.count('ñ')
        char_kword = 0
        if len(kword) > nys_kword:
            char_kword = len(kword) - nys_kword
        num_char += char_kword
        num_nys += nys_kword
    return (6 * num_nys + num_char) + (3 * num_keywords + 110)


def check_sizes(keyword_list):
    """Check if size of some keyword is more than 1024."""
    for kword in keyword_list:
        if len(kword) > 1024:
            return False
    return True


def gen_keyword_list(char, size_kword, num_kwords):
    """Debug function: return a test keywords list."""
    keywords_list = []
    for _ in range(num_kwords):
        kword = char * size_kword
        keywords_list.append(kword)
    return keywords_list

def save_keywords(keywords_list):
    with open('keyword_list2.txt', 'w') as f:
        for item in keywords_list:
            f.write("%s\n" % item)


def main():
    """Load audios, make transcripts using 'IBM SST' service and after save them in JSON folder."""
    api_key, url_service = load_env('.env')
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url_service)

    keywords_list = extract_keywords('keywords.xlsx', 4)
    print(f'Size of keywords_list: {len(keywords_list)}')

    audios_folder = "audios"
    #transcripts_folder = "transcripts"
    for audio_file in os.listdir(audios_folder):
        audio_pathfile = os.path.join(audios_folder, audio_file)
        print(audio_pathfile)
        if os.path.isfile(audio_pathfile):
            sst_response(audio_pathfile, speech_to_text, keywords_list)
            #save_json(data_json, audio_file, transcripts_folder)


if __name__ == '__main__':
    main()
