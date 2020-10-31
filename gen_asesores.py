#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gen asesores data"""

import os
import json
import datetime
import pandas as pd
import pymysql
import re


def load_json(json_pathfile):
    """Load JSON file."""
    with open(json_pathfile) as json_file:
        string_json = json_file.read()
        string_json = string_json.replace('\t', '').replace('\n', ' ')
        data_json = json.loads(string_json)
    return data_json


def get_metadata(json_file):
    labels = json_file.split('_')
    campaing = labels[0]
    dni = labels[4]
    date = labels[1].split('-')
    hour = date[1][:2]
    return campaing, dni, hour


def db_to_df(db_env, sql_statement):
    """Extract a dataframe from a db table."""
    print("Connecting to '{}' db...".format(db_env['db']))
    connection = pymysql.connect(host=db_env['host'],
                                 user=db_env['user'],
                                 password=db_env['password'],
                                 db=db_env['db'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            sql_df = pd.DataFrame(cursor.fetchall())
    finally:
        connection.close()

    return sql_df


def get_speakers(data_json):
    speaker_labels = data_json['speaker_labels']
    speakers = set()
    for elem in speaker_labels:
        speaker_num = elem['speaker']
        if speaker_num not in speakers:
            speakers.add(speaker_num)
    return speakers


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
            speaker_current = find_speaker(speaker_labels, from_time, to_time)

            if speaker_current == speaker:
                text_speaker += f"{word} "
            else:
                text_speaker = text_speaker.strip()
                conversation.append([init_text_time, speaker, text_speaker, to_time])
                text_speaker = f"{word} "
                speaker = speaker_current
                init_text_time = from_time
    text_speaker = text_speaker.strip()
    conversation.append((init_text_time, speaker, text_speaker, to_time)) #Adding last line
    return conversation


def extract_transcripts_words(conversation, speakers):
    speaker_transcripts = {}
    speaker_words = {}
    for speaker in speakers:
        transcripts_by_speaker = []
        words_by_speaker = ''
        for line in conversation:
            if line[1] == speaker:
                transcript = line[2]
                transcripts_by_speaker.append(transcript)
                words_by_speaker += ' ' + transcript
        speaker_transcripts[speaker] = transcripts_by_speaker
        speaker_words[speaker] = words_by_speaker.strip()
    
    return speaker_transcripts, speaker_words

def determine_roles(speaker_words, keywords):
    speaker_num_words = {}
    for speaker in speaker_words:
        words = speaker_words[speaker].split(' ')
        speaker_num_words[speaker] = len(words)
    #print(speaker_num_words)
    #asesor = max(speaker_num_words, key=speaker_num_words.get)  # Just use 'min' instead of 'max' for minimum.

    speaker_num_matches = {}
    for speaker in speaker_words:
        words = speaker_words[speaker]
        total_matches = 0
        for keyword in keywords:
            matches = re.findall(keyword, words)
            total_matches += len(matches)
        speaker_num_matches[speaker] = total_matches
    #print(speaker_num_matches)

    talkative1 = max(speaker_num_words, key=speaker_num_words.get)
    talkative2 = max(speaker_num_matches, key=speaker_num_matches.get)

    speaker_roles = {}
    if talkative1 == talkative2:
        #print('Asesor found!')
        speaker_roles[speaker] = 'asesor'
    else:
        print('ERROR! Asesor not found!')
        print(speaker_num_words)
        print(speaker_num_matches)
        print('\n')


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
            speaker = find_speaker(speaker_labels, start_time, end_time)
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
    #asesores = pd.DataFrame(columns=['dni','hour','gender','number of words','top words'])
    db_env = {'host':'158.177.190.81', 'user':'andres', 'password':'vd3VdcXQBRhD','db':'isadatastage','port':'3306'}
    db_table = "asesores"
    sql_statement = "SELECT * FROM {}".format(db_table)
    print(db_env)
    asesores_df = db_to_df(db_env, sql_statement)
    #print(asesores_df)
    for json_file in os.listdir('json'):
        json_pathfile = os.path.join('json', json_file)
        if os.path.isfile(json_pathfile):
            print("\n{}".format(json_file))
            campaing, dni, hour = get_metadata(json_file)
            asesores_dict = asesores_df.set_index('identificacion').T.to_dict('list')
            name = asesores_dict[dni][1]
            gender = asesores_dict[dni][3]
            print("{}, {}, {}, {}, {}".format(dni, name, gender, campaing, hour))
            data_json = load_json(json_pathfile)
            speakers = get_speakers(data_json)
            conversation = extract_conversation(data_json)
            _, speaker_words = extract_transcripts_words(conversation, speakers)
            keywords = ['IGS', 'bancolombia']
            determine_roles(speaker_words, keywords)
            #keywords_found = extract_keywords(data_json)
            #save_extracted_data(conversation, json_file, "conversations", "conv")
            #save_extracted_data(keywords_found, json_file, "keywords_found", "kwds")


if __name__ == '__main__':
    main()
