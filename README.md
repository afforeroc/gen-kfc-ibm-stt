# Demostration using IBM Speech to Text service

## System requeriments (recommended)
* Ubuntu 20.04 LTS

## 1. Configuration

1.1 Install the stable/latest version of Python 3 and verify their version.
```
$ sudo apt install python3
```
```
$ python3 --version
```

1.2 Install pip and verify their version.
```
$ sudo apt install python3-pip
```
```
$ pip3 --version
```

1.3 Install necessary Python libraries.
```
$ pip3 install --upgrade "ibm-watson>=4.5.0"
$ pip3 install pandas xlrd
$ pip3 install python-dotenv
```

## 2. Configure the enviroment
2.1 Create an instance of [IBM Speech to text](https://www.ibm.com/cloud/watson-speech-to-text) service.

2.2 Obtain the `api_key` and `url_service` of IBM STT service and put them on `new.env` file.
After rename `new.env` file to `.env` file.

2.4 Please put all audio files in `audios/` folder.

## 3. Execution

3.1 Run the first app to obtain transcripts from audios files. The transcripts will be store in `transcripts/` folder. The generated files will have the same name of source audio files with `*.json` extension.
```
$ python3 obtain_transcripts.py
```

3.2 Run the second app to generate conversations from transcripts files. The conversations will be store in `conversations/` folder. The generated files will have the same name of source audio files with `*.json` extension.
```
$ python3 construct_conversations.py
```

3.3 Enjoy ;)

## References links
* [IBM Cloud API Docs: Python SDK of IBM Watson™ STT](https://cloud.ibm.com/apidocs/speech-to-text?code=python)
* [IBM Watson APIs: Python SDK of IBM Watson™ STT](https://github.com/watson-developer-cloud/python-sdk/blob/master/examples/speech_to_text_v1.py)
