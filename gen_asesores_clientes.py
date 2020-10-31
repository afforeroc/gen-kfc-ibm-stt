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
    asesor_dni = labels[4]
    date = labels[1].split('-')
    hour = date[1][:2]
    cliente_phone, _ = labels[5].split('-')
    return campaing, asesor_dni, hour, cliente_phone


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


def words_by_roles(speaker_words, keywords=None):
    speaker_num_words = {}
    for speaker in speaker_words:
        words = speaker_words[speaker].split(' ')
        speaker_num_words[speaker] = len(words)
    asesor = max(speaker_num_words, key=speaker_num_words.get)
    cliente = min(speaker_num_words, key=speaker_num_words.get)
    
    """
    speaker_num_matches = {}
    for speaker in speaker_words:
        words = speaker_words[speaker]
        total_matches = 0
        for keyword in keywords:
            matches = re.findall(keyword, words)
            total_matches += len(matches)
        speaker_num_matches[speaker] = total_matches
    #print(speaker_num_matches)
    """

    asesor_words = speaker_words[asesor]
    cliente_words = speaker_words[cliente]
    return asesor_words, cliente_words


def get_asesor(dni, name, gender, campaing, hour, words=None):
    row_asesor = {}
    row_asesor['dni'] = dni
    row_asesor['name'] = name
    row_asesor['gender'] = gender
    row_asesor['campaing'] = campaing
    row_asesor['hour'] = hour
    row_asesor['words'] = words
    return row_asesor


def get_cliente(telefono, hour, cliente_words):
    row_cliente = {}
    row_cliente['telefono'] = telefono
    row_cliente['hour'] = hour
    row_cliente['words'] = cliente_words
    return row_cliente


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
    print("All data extracted from db!")
    
    asesores_analytics_df = pd.DataFrame(columns = ['dni', 'name', 'gender', 'campaing', 'hour', 'words'])
    clientes_analytics_df = pd.DataFrame(columns = ['telefono', 'hour', 'words'])

    for json_file in os.listdir('json'):
        json_pathfile = os.path.join('json', json_file)
        if os.path.isfile(json_pathfile):
            print("\n{}".format(json_file))

            # extract all metadata labels
            campaing, asesor_dni, hour, cliente_phone = get_metadata(json_file)
            asesores_dict = asesores_df.set_index('identificacion').T.to_dict('list')
            
            # extract data asesor
            asesor_name = asesores_dict[asesor_dni][1]
            asesor_gender = asesores_dict[asesor_dni][3]

            data_json = load_json(json_pathfile)
            speakers = get_speakers(data_json)
            conversation = extract_conversation(data_json)
            _, speaker_words = extract_transcripts_words(conversation, speakers)
            
            asesor_words, cliente_words = words_by_roles(speaker_words)
            
            asesor_row = get_asesor(asesor_dni, asesor_name, asesor_gender, campaing, hour, asesor_words)
            cliente_row = get_cliente(cliente_phone, hour, cliente_words)
            asesores_analytics_df = asesores_analytics_df.append(asesor_row, ignore_index=True)
            clientes_analytics_df = clientes_analytics_df.append(cliente_row, ignore_index=True)

    # Save data of analytics
    asesores_analytics_df.to_excel("asesores_analytics.xlsx", index=False)
    clientes_analytics_df.to_excel("clientes_analytics.xlsx", index=False)


if __name__ == '__main__':
    main()
