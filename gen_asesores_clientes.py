#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gen asesores data"""

import os
import json
import datetime
import pandas as pd
import pymysql
import re
import sys
import time
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stop_words = stopwords.words('spanish')


def load_json(json_pathfile):
    """Load JSON file."""
    with open(json_pathfile) as json_file:
        string_json = json_file.read()
        string_json = string_json.replace('\t', '').replace('\n', ' ')
        data_json = json.loads(string_json)
    return data_json


def get_metadata(json_file, tags):
    labels = json_file.split('_')
    if len(labels) != len(tags):
        print('Missing labels')
        sys.exit(1)
    metadata = {}
    for i, elem in enumerate(tags):
        metadata[elem] = labels[i]
    
    phone, _ = metadata['customer_phone'].split('-')
    metadata['customer_phone'] = phone
    return metadata


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

def remove_stop_words(words_by_speaker):
    word_tokens = word_tokenize(words_by_speaker.strip())
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    filtered_sentence = []
    for w in word_tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w)
    return ' '.join(filtered_sentence)

def extract_transcripts_words(conversation, speakers):
    #speaker_transcripts = {}
    speaker_words = {}
    for speaker in speakers:
        #transcripts_by_speaker = []
        words_by_speaker = ''
        for line in conversation:
            if line[1] == speaker:
                #transcripts_by_speaker.append(line[2])
                words_by_speaker += ' ' + line[2]
        #speaker_transcripts[speaker] = transcripts_by_speaker
        words_by_speaker = words_by_speaker.strip()
        words_by_speaker = remove_stop_words(words_by_speaker)
        speaker_words[speaker] = words_by_speaker
        return speaker_words


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


def get_assessor(assessors, metadata, assessor_words):
    row_assessor = {}
    row_assessor['dni'] = metadata['assessor_dni']
    row_assessor['name'] = assessors[metadata['assessor_dni']][1]
    row_assessor['gender'] = assessors[metadata['assessor_dni']][3]
    row_assessor['campaign'] = metadata['campaign']
    date, time = metadata['datetime'].split('-')
    row_assessor['date'] = date
    row_assessor['time'] = time
    row_assessor['words'] = assessor_words
    return row_assessor


def get_customer(metadata, customer_words):
    row_customer = {}
    row_customer['phone'] = metadata['customer_phone']
    date, time = metadata['datetime'].split('-')
    row_customer['date'] = date
    row_customer['time'] = time
    row_customer['words'] = customer_words
    return row_customer


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
    asesores_df = db_to_df(db_env, sql_statement)
    print("All data extracted from db!")
    
    asesores_analytics_df = pd.DataFrame(columns = ['campaign', 'dni', 'name', 'gender', 'date', 'time', 'words'])
    clientes_analytics_df = pd.DataFrame(columns = ['phone', 'date', 'time', 'words'])

    
    #print(sr)

    total_files = len(os.listdir('json'))
    count = 0
    t0 = time.time()
    for json_file in os.listdir('json'):
        json_pathfile = os.path.join('json', json_file)
        if os.path.isfile(json_pathfile):

            # extract all metadata tags
            tags = ['campaign', 'datetime', 'lead_id', 'epoch', 'assessor_dni', 'customer_phone']
            metadata = get_metadata(json_file, tags)
            assessors = asesores_df.set_index('identificacion').T.to_dict('list')
            
            # extract data asesor
            data_json = load_json(json_pathfile)
            speakers = get_speakers(data_json)
            conversation = extract_conversation(data_json)
            speaker_words = extract_transcripts_words(conversation, speakers)
            assessor_words, customer_words = words_by_roles(speaker_words)

            assessor_row = get_assessor(assessors, metadata, assessor_words)
            customer_row = get_customer(metadata, customer_words)

            asesores_analytics_df = asesores_analytics_df.append(assessor_row, ignore_index=True)
            clientes_analytics_df = clientes_analytics_df.append(customer_row, ignore_index=True)
            count += 1
            porcentage = count*100/total_files
            print("{:.2f}%, {}".format(porcentage, json_file))

    # Save data of analytics
    asesores_analytics_df.to_excel("asesores_analytics.xlsx", index=False)
    clientes_analytics_df.to_excel("clientes_analytics.xlsx", index=False)
    t1 = time.time() - t0
    print("Time elapsed: {:.2f}s".format(t1)) # CPU seconds elapsed (floating point)


if __name__ == '__main__':
    main()
