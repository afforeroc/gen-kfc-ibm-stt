# IBM Speech to Text Demo

## System requeriments
* Ubuntu 20.04 LTS

## 1. Software configuration
1.1 Install the latest version of `python3` and verify their version.
```
$ sudo apt install python3
```
```
$ python3 --version
```

1.2 Install `pip3` and verify their version.
```
$ sudo apt install python3-pip
```
```
$ pip3 --version
```

1.3 Install necessary libraries and IBM SDK for python3.
```
$ pip3 install python-dotenv pandas xlrd
```
```
$ pip3 install --upgrade "ibm-watson>=4.5.0"
```

## 2. Enviroment configuration
2.1 Create an instance of [IBM Speech to text](https://www.ibm.com/cloud/watson-speech-to-text) service.

2.2 Obtain the `API_KEY` and `API_URL` of IBM STT service and put them on `new.env` file. After rename `new.env` file to `.env` file.

2.3 Please put all audio files in `audios/` folder.

## 3. Execution
3.1 Run the first app to obtain json responses from audios files. These response will be store in `json/` folder. The generated files will have the same name of source audio files with `*.json` extension.
```
$ python3 sync_obtain_json.py
```

3.2 Run the second app to generate conversations from transcripts files. The conversations will be store in `conversations/` folder. The generated files will have the same name of source audio files with `*.txt` extension.
```
$ python3 make_conversation.py
```

## References links
* [IBM Cloud API Docs: Python SDK of IBM Watson™ STT](https://cloud.ibm.com/apidocs/speech-to-text?code=python)
* [IBM Watson APIs: Python SDK of IBM Watson™ STT](https://github.com/watson-developer-cloud/python-sdk/blob/master/examples/speech_to_text_v1.py)
