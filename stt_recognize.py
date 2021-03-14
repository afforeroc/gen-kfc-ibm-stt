#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obtain JSON responses from 'IBM SST' audio processing."""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def get_env(env_filepath, campaign, key):
    """Get env settings of a campaign."""
    f = open(env_filepath)
    data = json.load(f)
    f.close()
    if campaign in data:
        env = (data[campaign])[key]
    else:
        print('{} campaign does not exist'.format(campaign))
        sys.exit(1)
    return env


def instantiate_stt(stt_env):
    """Instantiate an IBM Speech To Text API."""
    authenticator = IAMAuthenticator(stt_env['api_key'])
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(stt_env['api_url'])
    return stt


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
    print("{} {} was saved sucessful".format(get_current_time(), json_pathfile))


def sst_response(audio_pathfile, speech_to_text, ibm_stt_env, keywords, custom_id=None):
    """Return callback response of SST using one audiofile."""
    with open(audio_pathfile, 'rb') as audio_file:
        response = speech_to_text.recognize(audio=audio_file,
                                            content_type='audio/mp3',
                                            model=ibm_stt_env["model"],
                                            keywords=keywords,
                                            word_alternatives_threshold=0.6,
                                            keywords_threshold=ibm_stt_env["keywords_threshold"],
                                            language_customization_id=ibm_stt_env["language_customization_id"],
                                            speaker_labels=True,
                                            inactivity_timeout=-1,
                                            max_alternatives=3).get_result()
    return response

def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def main():
    """Obtain JSON responses from 'IBM SST' audio processing."""
    campaign = sys.argv[1] # e.g. igs_bancolombia_co
    keywords_filepath = sys.argv[2] # excel-basekeywords/Bancolombia_basekeywords_2020-10-30.xlsx
    ibm_stt_env = get_env('config/default.json', campaign, 'ibm_stt')
    speech_to_text = instantiate_stt(ibm_stt_env)
    audios_folder = "audios"
    json_folder = "json"
    keywords = extract_keywords(keywords_filepath, 0)
    for audio_file in os.listdir(audios_folder):
        audio_pathfile = os.path.join(audios_folder, audio_file)
        if os.path.isfile(audio_pathfile):
            print("{} {}".format(get_current_time(), audio_file))
            data_json = sst_response(audio_pathfile, speech_to_text, ibm_stt_env, keywords)
            save_json(data_json, audio_file, json_folder)


if __name__ == '__main__':
    main()
