#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construct conversations from STT responses of IBM service."""

import os
import json
import datetime


def load_json(json_pathfile):
    """Load JSON file."""
    with open(json_pathfile) as json_file:
        string_json = json_file.read()
        string_json = string_json.replace('\t', '').replace('\n', ' ')
        data_json = json.loads(string_json)
    return data_json


def find_speaker(from_time, speaker_labels):
    """Return the number of speaker."""
    speaker = -1
    for sp_block in speaker_labels:
        if sp_block['from'] == from_time:
            speaker = sp_block['speaker']
        elif abs(sp_block['from'] - from_time) <= 0.01:
            speaker = sp_block['speaker']
    return speaker


def get_time(num_seconds):
    time = datetime.timedelta(seconds=float(num_seconds+0.000001))
    return str(time)[:-4]


def extract_conversation(data_json):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = data_json['results']
    speaker_labels = data_json['speaker_labels']
    # Only once
    conversation = []
    init_text_time = data_json['speaker_labels'][0]['from']
    speaker = data_json['speaker_labels'][0]['speaker']
    text_speaker = ""
    # For all results
    for result in results:
        timestamps = result['alternatives'][0]['timestamps']
        for timestamp in timestamps:
            word = timestamp[0]
            from_time = timestamp[1]
            to_time = timestamp[2]
            speaker_current = find_speaker(from_time, speaker_labels)

            if speaker_current == speaker:
                text_speaker += f"{word} "
            else:
                conversation.append([init_text_time, speaker, text_speaker, to_time])
                text_speaker = f"{word} "
                speaker = speaker_current
                init_text_time = from_time
    conversation.append((init_text_time, speaker, text_speaker, to_time)) #Adding last line
    return conversation


def extract_keywords(data_json):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = data_json['results']
    speaker_labels = data_json['speaker_labels']
    keywords_found = []
    for result in results:
        keywords_result = result['keywords_result']
        for keyword in keywords_result:
            start_time = keywords_result[keyword][0]['start_time']
            end_time = keywords_result[keyword][0]['end_time']
            speaker = find_speaker(start_time, speaker_labels)
            if speaker == -1:
                print('ERROR', keyword, start_time, speaker)
            keywords_found.append((start_time, speaker, keyword, end_time))
    return keywords_found


def save_extracted_data(keywords_found, json_file, folder, label):
    """Save conversation in '*.txt' file."""
    name_file = os.path.splitext(json_file)[0]
    filepath = f'{folder}/{label}_{name_file}.txt'
    filepath_rw = open(filepath, 'w+')
    for elem in keywords_found:
        filepath_rw.write("[{}] - Speaker {}: {} - [{}]\n\n".format(get_time(elem[0]), elem[1], elem[2], get_time(elem[3])))
    filepath_rw.close()


def main():
    """Load JSON files, construct the dialogue and after save them in 'conversations' folder."""
    for json_file in os.listdir('json'):
        json_pathfile = os.path.join('json', json_file)
        if os.path.isfile(json_pathfile):
            print(json_pathfile)
            data_json = load_json(json_pathfile)
            conversation = extract_conversation(data_json)
            keywords_found = extract_keywords(data_json)
            save_extracted_data(conversation, json_file, "conversations", "conv")
            save_extracted_data(keywords_found, json_file, "keywords_found", "kwds")


if __name__ == '__main__':
    main()
