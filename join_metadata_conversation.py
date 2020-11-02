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
        json_data = json.loads(string_json)
    return json_data


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
    time = datetime.timedelta(seconds=float(num_seconds+0.000001))
    return str(time)[:-4]


def get_conversation(json_filename, json_data):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = json_data['results']
    speaker_labels = json_data['speaker_labels']
    # Only once
    columns = ['speaker', 'start_time', 'end_time', 'start_time_std', 'end_time_std',  'transcript']
    conversation_by_call = pd.DataFrame(columns=columns)
    print(conversation_by_call)

    init_text_time = json_data['speaker_labels'][0]['from']
    final_text_time = json_data['speaker_labels'][1]['to']
    speaker = json_data['speaker_labels'][0]['speaker']
    transcript = ""
    count = 0
    # For all results
    for result in results:
        timestamps = result['alternatives'][0]['timestamps']
        for timestamp in timestamps:
            word = timestamp[0]
            from_time = timestamp[1]
            to_time = timestamp[2]
            speaker_current = find_speaker(speaker_labels, from_time, to_time)
            if speaker_current == speaker:
                transcript += f"{word} "
                final_text_time = to_time
            else:
                transcript = transcript.strip()
                #print("{} | {} | {} | {}".format(init_text_time, speaker, transcript, to_time))
                conversation_line = pd.DataFrame({"speaker":speaker, "start_time":init_text_time, "end_time":final_text_time, "start_time_std":get_time(init_text_time), "end_time_std":get_time(final_text_time), "transcript":transcript}, index=[1])
                #print(conversation_line)
                conversation_by_call = conversation_by_call.append(conversation_line, ignore_index=True)
                transcript = f"{word} "
                speaker = speaker_current
                init_text_time = from_time
                final_text_time = to_time
                
    transcript = transcript.strip()
    conversation_line = pd.DataFrame({"speaker":speaker, "start_time":init_text_time, "end_time":final_text_time, "start_time_std":get_time(init_text_time), "end_time_std":get_time(final_text_time), "transcript":transcript}, index=[1])
    conversation_by_call = conversation_by_call.append(conversation_line, ignore_index=True) #Adding last line
    return conversation_by_call


def extract_keywords(json_data, json_file):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    #print(json_data)
    results = json_data['results']
    speaker_labels = json_data['speaker_labels']
    keywords_found = []
    for result in results:
        #print("result = ", result)
        if 'keywords_result' in result:
            keywords_result = result['keywords_result']
            for keyword in keywords_result:
                start_time = keywords_result[keyword][0]['start_time']
                end_time = keywords_result[keyword][0]['end_time']
                speaker = find_speaker(speaker_labels, start_time, end_time)
                if speaker == -1:
                    print('ERROR', keyword, start_time, speaker)
                    print()
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
    columns = ['campaign', 'assessor_dni', 'assesor_name', 
                'assesor_gender', 'customer_phone',
                'date', 'time', 'speaker', 
                'start_time', 'transcript', 'end_time', ]
    #analytics_df = pd.DataFrame(columns=columns)
    for json_filename in os.listdir('json'):
        json_filepath = os.path.join('json', json_filename)
        if os.path.isfile(json_filepath):
            print(json_filename)
            json_data = load_json(json_filepath)
            conversation_by_call = get_conversation(json_filename, json_data)
            print(conversation_by_call)
            conversation_by_call.to_excel("analytics-demo.xlsx", index=False)
            break
            #keywords_found = extract_keywords(json_data, json_file)
            #save_extracted_data(conversation, json_file, "conversations", "conv")
            #save_extracted_data(keywords_found, json_file, "keywords_found", "kwds")


if __name__ == '__main__':
    main()
