#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Join metadata from filename and data from json (IBM STT response)."""

import os
import sys
import time
import json
import datetime
import pandas as pd
import pymysql


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


def get_metadata(json_filename, tags):
    labels = json_filename.split('_')
    if len(labels) != len(tags):
        print('Missing labels')
        sys.exit(1)
    metadata = {}
    for i, elem in enumerate(tags):
        metadata[elem] = labels[i]

    phone, _ = metadata['customer_phone'].split('-')
    metadata['customer_phone'] = phone
    metadata['keyfile'], _ = json_filename.split('.')
    return metadata


def get_assessor(assessors, metadata):
    assessor = {}
    assessor['name'] = assessors[metadata['assessor_dni']][1]
    assessor['gender'] = assessors[metadata['assessor_dni']][3]
    return assessor


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
    time_f = datetime.timedelta(seconds=float(num_seconds + 0.000001))
    return str(time_f)[:-4]


def get_time_std(hhmmss):
    hh = hhmmss[:2]
    mm = hhmmss[2:4]
    ss = hhmmss[4:]
    hhmmss_std = "{}:{}:{}".format(hh, mm, ss)
    return hhmmss_std


def get_data_by_call(metadata, assessor, json_data):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = json_data['results']
    speaker_labels = json_data['speaker_labels']
    # Only once
    columns = [
        'keyfile', 'campaign', 'assessor_dni', 'assesor_name',
        'assesor_gender', 'customer_phone', 'date', 'time', 'speaker',
        'start_time', 'end_time', 'start_time_std', 'end_time_std',
        'transcript'
    ]
    conversation_by_call = pd.DataFrame(columns=columns)

    init_text_time = json_data['speaker_labels'][0]['from']
    final_text_time = json_data['speaker_labels'][1]['to']
    speaker = json_data['speaker_labels'][0]['speaker']
    transcript = ""
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
                date, time_f = metadata['datetime'].split('-')
                conversation_line = pd.DataFrame(
                    {
                        'keyfile': metadata['keyfile'],
                        'campaign': metadata['campaign'],
                        'assessor_dni': metadata['assessor_dni'],
                        'assesor_name': assessor['name'],
                        'assesor_gender': assessor['gender'],
                        'customer_phone': metadata['customer_phone'],
                        'date': date,
                        'time': get_time_std(time_f),
                        'speaker': speaker,
                        'start_time': init_text_time,
                        'end_time': final_text_time,
                        'start_time_std': get_time(init_text_time),
                        'end_time_std': get_time(final_text_time),
                        'transcript': transcript
                    },
                    index=[1])
                #print(conversation_line)
                conversation_by_call = conversation_by_call.append(
                    conversation_line, ignore_index=True)
                transcript = f"{word} "
                speaker = speaker_current
                init_text_time = from_time
                final_text_time = to_time

    transcript = transcript.strip()
    conversation_line = pd.DataFrame(
        {
            'keyfile': metadata['keyfile'],
            'campaign': metadata['campaign'],
            'assessor_dni': metadata['assessor_dni'],
            'assesor_name': assessor['name'],
            'assesor_gender': assessor['gender'],
            'customer_phone': metadata['customer_phone'],
            'date': date,
            'time': get_time_std(time_f),
            'speaker': speaker,
            'start_time': init_text_time,
            'end_time': final_text_time,
            'start_time_std': get_time(init_text_time),
            'end_time_std': get_time(final_text_time),
            'transcript': transcript
        },
        index=[1])
    conversation_by_call = conversation_by_call.append(
        conversation_line, ignore_index=True)  #Adding last line
    return conversation_by_call


def main():
    """Load JSON files, construct the dialogue and after save them in 'conversations' folder."""

    # Extrac information from asesores db table
    db_env = {
        'host': '158.177.190.81',
        'user': 'andres',
        'password': 'vd3VdcXQBRhD',
        'db': 'isadatastage',
        'port': '3306'
    }
    db_table = "asesores"
    sql_statement = "SELECT * FROM {}".format(db_table)
    asesores_df = db_to_df(db_env, sql_statement)
    print("All data extracted from db!")
    assessors = asesores_df.set_index('identificacion').T.to_dict('list')

    # Create the big dataframe
    columns = [
        'keyfile', 'campaign', 'assessor_dni', 'assesor_name',
        'assesor_gender', 'customer_phone', 'date', 'time', 'speaker',
        'start_time', 'end_time', 'start_time_std', 'end_time_std',
        'transcript'
    ]
    analytics_df = pd.DataFrame(columns=columns)

    # Define the tags of filename
    tags = [
        'campaign', 'datetime', 'lead_id', 'epoch', 'assessor_dni',
        'customer_phone'
    ]

    # Init performance control
    total_files = len(os.listdir('json'))
    count = 0
    init_time = time.time()

    # Iterate extracting metadata and json data (file by file)
    for json_filename in os.listdir('json'):
        json_filepath = os.path.join('json', json_filename)
        if os.path.isfile(json_filepath):

            # Extract metadata from filename
            metadata = get_metadata(json_filename, tags)

            # Extract assessor data
            assessor = get_assessor(assessors, metadata)

            # Load JSON data
            json_data = load_json(json_filepath)

            # Construct conversation
            data_by_call = get_data_by_call(metadata, assessor, json_data)

            # Append the data by call to big dataframe
            analytics_df = analytics_df.append(data_by_call)

            # Calculate porcentage of files processed
            count += 1
            porcentage = count * 100 / total_files
            print("{:.2f}%, {}".format(porcentage, json_filename))

    # Save dataframe
    analytics_df.to_excel("dataframe.xlsx", index=False)

    # Show execution time (seconds)
    exec_time = time.time() - init_time
    print("Time elapsed: {:.2f}s".format(exec_time))


if __name__ == '__main__':
    main()
