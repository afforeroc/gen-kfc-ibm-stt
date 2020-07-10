import json


def load_data_json():
    with open ("json/data.json") as json_file:
        json_string = json_file.read()
        json_string = json_string.replace('\t', '').replace('\n', ' ')
        data = json.loads(json_string)
    return data


def find_speaker(init_time, speaker_labels):
    for sp_block in speaker_labels:
        if sp_block['from'] == init_time:
            return str(sp_block['speaker'])


def extract_conversation(data):
    results = data['results']
    speaker_labels = data['speaker_labels']
    speakers = set()
    speaker_text = ""
    # Only once
    first_time = results[0]['alternatives'][0]['timestamps'][0][1]
    speaker_prev = find_speaker(first_time, speaker_labels)
    speakers.add(speaker_prev)
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
                if speaker_current not in speakers:
                    speakers.add(speaker_current)
            speaker_prev = speaker_current
    return conversation

def save_conversation(conversation):
    f = open('conversations/conversation.txt', 'w+')
    for line in conversation:
        f.write('speaker ' + line[0] + ': ' + line[1] + '\n')
    f.close()


def main():
    data = load_data_json()
    conversation = extract_conversation(data)
    print(conversation)
    save_conversation(conversation)


if __name__ == '__main__':
    main()
