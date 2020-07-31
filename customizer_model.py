#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Customizer models for a IBM Speech To Text instance."""

import os
import json
from dotenv import load_dotenv
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def load_env(env_file):
    """Load authentication settings for SST service."""
    dotenv_path = os.path.join(os.path.dirname(__file__), env_file)
    load_dotenv(dotenv_path)
    api_key = os.getenv('API_KEY')
    url_service = os.getenv('API_URL')
    return api_key, url_service


def instantiate_stt(api_key, url_service):
    """Link a SDK instance with a IBM STT instance."""
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url_service)
    return speech_to_text


def custom_language_model_run(speech_to_text, operation, custom_id=None, base_model_name=None, dialect=None):
    """Custom language model operations."""
    if operation == "create model":
        language_model = speech_to_text.create_language_model(
        base_model_name, dialect, description=base_model_name).get_result()
        print(json.dumps(language_model, indent=2))
    elif operation == "list models":
        language_models = speech_to_text.list_language_models().get_result()
        print(json.dumps(language_models, indent=2))
    elif operation == "get model":
        language_model = speech_to_text.get_language_model(custom_id).get_result()
        print(json.dumps(language_model, indent=2))
    elif operation == "delete model":
        speech_to_text.delete_language_model(custom_id)
    elif operation == "train model":
        speech_to_text.train_language_model(custom_id)
    elif operation == "reset model":
        speech_to_text.reset_language_model(custom_id)
    elif operation == "upgrade model":
        speech_to_text.upgrade_language_model(custom_id)
    else:
        print(f"The '{operation}' operation is not valid.")


def corpora_run(speech_to_text, operation, custom_id, corpus_name=None, corpus_pathfile=None):
    """Corpora operations of a custom language model."""
    if operation == "list corpora":
        corpora = speech_to_text.list_corpora(custom_id).get_result()
        print(json.dumps(corpora, indent=2))
    elif operation == "add corpus":
        with open(corpus_pathfile, 'rb') as corpus_file:
            speech_to_text.add_corpus(
                custom_id,
                corpus_name,
                corpus_file,
                allow_overwrite=True,
            )
    elif operation == "get corpus":
        corpus = speech_to_text.get_corpus(custom_id, corpus_name).get_result()
        print(json.dumps(corpus, indent=2))
    elif operation == "delete corpus":
        speech_to_text.delete_corpus(custom_id, corpus_name)
    else:
        print(f"The '{operation}' operation is not valid.")


def words_run(speech_to_text, operation, custom_id, word=None):
    """Words operations of a custom language model."""
    if operation == "list words":
        words = speech_to_text.list_words(custom_id).get_result()
        print(json.dumps(words, indent=2))
    elif operation == "add word":
        speech_to_text.add_word(custom_id, word)
    elif operation == "get word":
        word = speech_to_text.get_word(custom_id, word).get_result()
        print(json.dumps(word, indent=2))
    elif operation == "delete word":
        speech_to_text.delete_word(custom_id, word)
    else:
        print(f"The '{operation}' operation is not valid.")


def grammar_run(speech_to_text, custom_id, operation, grammar_name,  grammar_pathfile=None):
    """Grammar operations of a custom language model."""


    elif operation == "get grammar":
        grammar = speech_to_text.get_grammar(custom_id, grammar_name).get_result()
        print(json.dumps(grammar, indent=2))
    elif operation == "add grammar":
        with open(grammar_pathfile, 'rb') as grammar_file:
            speech_to_text.add_grammar(custom_id, grammar_name, grammar_file, 'application/srgs')
    elif operation == "delete grammar":
        speech_to_text.delete_grammar(custom_id, grammar_name)
    else:
        print(f"The '{operation}' operation is not valid.")


def create_custom_acoustic_model(speech_to_text, custom_acoustic, language):
    """Creates a new custom acoustic model for a specified base model."""
    acoustic_model = speech_to_text.create_acoustic_model(
        custom_acoustic, language, description=custom_acoustic).get_result()
    print(json.dumps(acoustic_model, indent=2))


def info_acoustic_models(speech_to_text):
    """Show all custom acoustic models."""
    acoustic_models = speech_to_text.list_acoustic_models().get_result()
    print("-- Acoustic models --")
    print(json.dumps(acoustic_models, indent=2))


def custom_acoustic_model_run(speech_to_text, custom_id, operation):
    """Custom acoustic model operations."""
    if operation == "get model":
        acoustic_model = speech_to_text.get_acoustic_model(custom_id).get_result()
        print(json.dumps(acoustic_model, indent=2))
    elif operation == "train model":
        speech_to_text.train_acoustic_model(custom_id)
    elif operation == "reset model":
        speech_to_text.reset_acoustic_model(custom_id)
    elif operation == "upgrade model":
        speech_to_text.upgrade_acoustic_model(custom_id)
    elif operation == "delete model":
        speech_to_text.delete_acoustic_model(custom_id)
    else:
        print(f"The '{operation}' operation is not valid.")

def audio_resource_run(speech_to_text, custom_id, operation):
    """Operations for audio resources of custom acoustic model."""
    if operation == "list audio":
        audio_resources = speech_to_text.list_audio(custom_id).get_result()
        print(json.dumps(audio_resources, indent=2))


def main():
    """Customizer of a STT IBM instance."""
    api_key, url_service = load_env('.env')
    speech_to_text = instantiate_stt(api_key, url_service)

    # -- Custom language models --

    #create_custom_language_model(speech_to_text,  "IGS lang model", "IGS lang model")
    #language_id = "7fa5d91f-be33-4903-9c26-8b0bdeb3fb2f"
    #info_custom_language_model(speech_to_text,  language_id)
    #custom_language_model_run(speech_to_text, language_id, "train model")
    #corpora_run(speech_to_text, language_id, "get corpus", "corpus_igs")
    #words_run(speech_to_text, language_id, "get word", "IGS")

    # -- Custom acoustic models --
    #create_custom_acoustic_model(speech_to_text, "Primer modelo acustico", "es-CO_NarrowbandModel")
    acoustic_id = "2dab4986-8c28-4f0c-bc0c-8bfafc64f966"
    #custom_acoustic_model_run(speech_to_text, custom_acoustic_id, "get model")
    audio_resource_run(speech_to_text, acoustic_id, "list audio")


if __name__ == '__main__':
    main()
