#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construct conversations from STT responses of IBM service."""

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
    return -1


def extract_conversation(data_json):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = data_json['results']
    speaker_labels = data_json['speaker_labels']
    # Only once
    conversation = []
    speaker_prev = 0
    text_speaker = ""
    # For all results
    for r_block in results:
        timestamps = r_block['alternatives'][0]['timestamps']
        for t_block in timestamps:
            init_time = t_block[1]
            word = t_block[0]
            speaker_current = find_speaker(init_time, speaker_labels)

            if speaker_current == speaker_prev:
                text_speaker += f'{word} '
            else:
                conversation.append([speaker_prev, text_speaker])
                text_speaker = f'{word} '
                speaker_prev = speaker_current

    conversation.append([speaker_prev,
                         text_speaker])  # Add the last line of speaker
    return conversation


def save_conversation(conversation, json_file, conversations_folder):
    """Save conversation in '*.txt' file."""
    name_file = os.path.splitext(json_file)[0]
    conversation_pathfile = f'{conversations_folder}/{name_file}.txt'
    conversation_file = open(conversation_pathfile, 'w+')
    for line in conversation:
        conversation_file.write('speaker ' + str(line[0]) + ': ' + line[1] +
                                '\n')
    conversation_file.close()


def main():
    """Load JSON files, construct the dialogue and after save them in 'conversations' folder."""
    transcripts_folder = "json"
    conversations_folder = "conversations"
    for json_file in os.listdir(transcripts_folder):
        json_pathfile = os.path.join(transcripts_folder, json_file)
        if os.path.isfile(json_pathfile):
            data_json = load_json(json_pathfile)
            conversation = extract_conversation(data_json)
            save_conversation(conversation, json_file, conversations_folder)


if __name__ == '__main__':
    main()
