import json
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
import os

# Load env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
URL_SERVICE = os.getenv("URL_SERVICE")

# Load SDK
authenticator = IAMAuthenticator(API_KEY)
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url(URL_SERVICE)

def save_json(data):
    with open("json/data.json","w", encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)

class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        json_data = json.dumps(data, indent=2, ensure_ascii=False).encode('utf8')
        save_json(data)
        print(json_data.decode())
        
    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

myRecognizeCallback = MyRecognizeCallback()

with open(join(dirname(__file__), './.', 'audios/sample2.mp3'), 'rb') as audio_file:
    audio_source = AudioSource(audio_file)
    speech_to_text.recognize_using_websocket(
        audio=audio_source,
        content_type='audio/mp3',
        recognize_callback=myRecognizeCallback,
        model='es-CO_NarrowbandModel',
        speaker_labels=True)
