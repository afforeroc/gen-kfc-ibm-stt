#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construct conversations from STT responses of IBM service."""

import os
import json
import datetime
import pandas as pd


def load_json(json_pathfile):
    """Load JSON file."""
    with open(json_pathfile) as json_file:
        string_json = json_file.read()
        string_json = string_json.replace('\t', '').replace('\n', ' ')
        data_json = json.loads(string_json)
    return data_json


def find_speaker(speaker_labels, from_time, to_time):
    """Return the number of speaker."""
    speaker = -1
    for sp_block in speaker_labels:
        if sp_block['from'] == from_time:
            speaker = sp_block['speaker']
        elif sp_block['to'] == to_time:
            speaker = sp_block['speaker']
        elif abs(sp_block['to'] - to_time) <= 0.01:
            speaker = sp_block['speaker']
    return speaker


def get_time(num_seconds):
    time = datetime.timedelta(seconds=float(num_seconds + 0.000001))
    return str(time)[:-4]


def get_conversation(json_data):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = json_data['results']
    speaker_labels = json_data['speaker_labels']
    # Only once
    conversation = []
    init_text_time = json_data['speaker_labels'][0]['from']
    final_text_time = json_data['speaker_labels'][1]['to']
    speaker = json_data['speaker_labels'][0]['speaker']
    text_speaker = ""
    # For all results
    for result in results:
        timestamps = result['alternatives'][0]['timestamps']
        for timestamp in timestamps:
            word = timestamp[0]
            from_time = timestamp[1]
            to_time = timestamp[2]
            speaker_current = find_speaker(speaker_labels, from_time, to_time)

            if speaker_current == speaker:
                text_speaker += f"{word} "
                final_text_time = to_time
            else:
                text_speaker = text_speaker.strip()
                conversation.append(
                    [init_text_time, speaker, text_speaker, final_text_time])
                text_speaker = f"{word} "
                speaker = speaker_current
                init_text_time = from_time
                final_text_time = to_time

    text_speaker = text_speaker.strip()
    conversation.append(
        [init_text_time, speaker, text_speaker,
         final_text_time])  #Adding last line
    return conversation


def get_conv_by_roles(conversation):
    speaker_numwords = {}
    for line in conversation:
        speaker = line[1]
        if speaker not in speaker_numwords:
            speaker_numwords[speaker] = len(line[2])
        else:
            speaker_numwords[speaker] += len(line[2])

    speakers = list(speaker_numwords.keys())

    assessor = max(speaker_numwords, key=speaker_numwords.get)
    client = min(speaker_numwords, key=speaker_numwords.get)

    speaker_rol = {}
    speaker_rol[assessor] = 'asesor'
    speaker_rol[client] = 'cliente'

    keywords = [
        "IGS", "bancolombia", "alianza", "calidad", "auditor", "auditora"
    ]

    for line in conversation:
        speaker = line[1]
        if speaker in speaker_rol:
            line[1] = speaker_rol[speaker]
        else:
            line[1] = 'asesor'

        transcript = line[2]
        if any(kwd in transcript for kwd in keywords):
            line[1] = 'asesor'
    return conversation, speakers, rol_speaker


def append_resume(dataframe_resume, filename, speakers, rol_speaker):
    dataframe_resume = dataframe_resume.append(
        {
            'keyfile': filename,
            'speakers': speakers,
            'asesor': rol_speaker['assessor'],
            'cliente': rol_speaker['client']
        },
        ignore_index=True)


def append_data(conversations_df, filename, conv_by_roles):
    for line in conv_by_roles:
        conversations_df = conversations_df.append(
            {
                'keyfile': filename,
                'speaker': line[1],
                'start_time': line[0], 
                'end_time': line[3], 
                'transcript': line[2]
            },
            ignore_index=True)
    return conversations_df


def save_extracted_data(keywords_found, json_filename, folder, label):
    """Save conversation in '*.txt' file."""
    filename = os.path.splitext(json_filename)[0]
    filepath = f'{folder}/{label}_{filename}.txt'
    filepath_rw = open(filepath, 'w+')
    for elem in keywords_found:
        filepath_rw.write("[{}] - {}: {} - [{}]\n\n".format(
            get_time(elem[0]), elem[1], elem[2], get_time(elem[3])))
    filepath_rw.close()


def main():
    """Construct conversation using roles: Assessor, Client and Auditor."""
    #dataframe_resume = pd.DataFrame(columns=['keyfile', 'speakers', 'asesor', 'cliente'])
    conversations_df = pd.DataFrame(columns=['keyfile', 'speaker', 'start_time', 'end_time', 'transcript'])

    for json_filename in os.listdir('json'):
        json_filepath = os.path.join('json', json_filename)
        if os.path.isfile(json_filepath):
            print(json_filepath)
            json_data = load_json(json_filepath)
            conv_pure = get_conversation(json_data)
            conv_by_roles, speakers, rol_speaker = get_conv_by_roles(conv_pure)
            filename = os.path.splitext(json_filename)[0]
            conversations_df = append_data(conversations_df, filename, conv_by_roles)
            #append_resume(dataframe_resume, filename, speakers, rol_speaker)
            save_extracted_data(conv_by_roles, json_filename, "conv-by-roles","cvr")
    #dataframe_resume.to_excel("dataframe100.xlsx", index=False)
    conversations_df.to_excel("conversations_100.xlsx", index=False)


if __name__ == '__main__':
    main()
