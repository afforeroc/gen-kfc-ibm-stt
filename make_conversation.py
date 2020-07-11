#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert various JSON files in coherent conversations."""

import os
import json


def load_json(json_pathfile):
    """Load JSON file."""
    with open(json_pathfile) as json_file:
        string_json = json_file.read()
        string_json = string_json.replace('\t', '').replace('\n', ' ')
        data_json = json.loads(string_json)
    return data_json


def find_speaker(init_time, speaker_labels):
    """Return the number of speaker."""
    for sp_block in speaker_labels:
        if sp_block['from'] == init_time:
            return sp_block['speaker']


def extract_conversation(data_json):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = data_json['results']
    speaker_labels = data_json['speaker_labels']
    speaker_text = ""
    # Only once
    first_time = results[0]['alternatives'][0]['timestamps'][0][1]
    speaker_prev = find_speaker(first_time, speaker_labels)
    conversation = []
    # For all results
    for r_block in results:
        timestamps = r_block['alternatives'][0]['timestamps']
        for t_block in timestamps:
            init_time = t_block[1]
            word = t_block[0]
            speaker_current = find_speaker(init_time, speaker_labels)
            if speaker_current == speaker_prev:
                speaker_text += f"{word} "
            else:
                conversation.append([speaker_prev, speaker_text])
                speaker_text = ""
                speaker_text += f"{word} "
            speaker_prev = speaker_current
    return conversation


def save_conversation(conversation, json_file):
    """Save conversation in '*.txt' file."""
    name_file = os.path.splitext(json_file)[0]
    conversation_pathfile = f'conversations/{name_file}.txt'
    conversation_file = open(conversation_pathfile, 'w+')
    for line in conversation:
        conversation_file.write('speaker ' + str(line[0]) + ': ' + line[1] + '\n')
    conversation_file.close()


def main():
    """Load JSON files, construct the dialogue and after save them in 'conversations' folder."""
    json_folder = "json"
    for json_file in os.listdir(json_folder):
        json_pathfile = os.path.join(json_folder, json_file)
        if os.path.isfile(json_pathfile):
            data_json = load_json(json_pathfile)
            conversation = extract_conversation(data_json)
            save_conversation(conversation, json_file)


if __name__ == '__main__':
    main()
