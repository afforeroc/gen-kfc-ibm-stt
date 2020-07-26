#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Customizer of a STT IBM instance."""

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


def create_custom_language_model(speech_to_text,  model_name, language_name):
    """Creates a new custom language model for a specified base model."""
    language_model = speech_to_text.create_language_model(
        model_name, language_name, description=model_name).get_result()
    print(json.dumps(language_model, indent=2))


def custom_model_operations(speech_to_text, custom_id, operation):
    """Various operations over a custom language model."""
    if operation == "list models":
        language_models = speech_to_text.list_language_models().get_result()
        print(json.dumps(language_models, indent=2))
    elif operation == "get model":
        language_model = speech_to_text.get_language_model(
            custom_id).get_result()
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


def add_corpus(speech_to_text, custom_id, corpus_pathfile, corpus_name):
    with open(corpus_pathfile, 'rb') as corpus_file:
        speech_to_text.add_corpus(
            custom_id,
            corpus_name,
            corpus_file,
            allow_overwrite=True,
        )


def corpora_operations(speech_to_text, custom_id, args):
    operation = args[0]
    if operation == "list corpora":
        corpora = speech_to_text.list_corpora(custom_id).get_result()
        print(json.dumps(corpora, indent=2))
    elif operation == "add corpus":
        corpus_name = args[1]
        corpus_pathfile = args[2]
        with open(corpus_pathfile, 'rb') as corpus_file:
            speech_to_text.add_corpus(
                custom_id,
                corpus_name,
                corpus_file,
                allow_overwrite=True,
            )
    elif operation == "get corpus":
        corpus_name = args[1]
        corpus = speech_to_text.get_corpus(custom_id, corpus_name).get_result()
        print(json.dumps(corpus, indent=2))
    elif operation == "delete corpus":
        corpus_name = args[1]
        speech_to_text.delete_corpus(custom_id, corpus_name)
    else:
        print(f"The '{operation}' operation is not valid.")


def words_operations(speech_to_text, custom_id, args):
    operation = args[0]
    if operation == "list words":
        words = speech_to_text.list_words(custom_id).get_result()
        print(json.dumps(words, indent=2))
    elif operation == "add word":
        speech_to_text.add_word(custom_id, args[1], sounds_like=args[2], display_as=args[3])
    elif operation == "get word":
        word = speech_to_text.get_word(custom_id, args[1]).get_result()
        print(json.dumps(word, indent=2))
    elif operation == "delete word":
        speech_to_text.delete_word(custom_id, args[1])
    else:
        print(f"The '{operation}' operation is not valid.")


def grammar_operations(speech_to_text, custom_id, args):
    if args[0] == "list grammars":
        grammars = speech_to_text.list_grammars(custom_id).get_result()
        print(json.dumps(grammars, indent=2))
    elif args[0] == "get grammar":
        grammar = speech_to_text.get_grammar(custom_id, args[1]).get_result()
        print(json.dumps(grammar, indent=2))
    elif args[0] == "delete grammar":
        speech_to_text.delete_grammar(custom_id, args[1])
    else:
        print(f"The '{args[0]}' operation is not valid.")


def add_grammar(speech_to_text, custom_id,  grammar_name, grammar_pathfile):
    with open(grammar_pathfile, 'rb') as grammar_file:
        speech_to_text.add_grammar(custom_id, grammar_name, grammar_file, 'application/srgs')


def main():
    """Customizer of a STT IBM instance."""
    api_key, url_service = load_env('.env')
    speech_to_text = instantiate_stt(api_key, url_service)

    # --- Language model ---
    custom_id = "7fa5d91f-be33-4903-9c26-8b0bdeb3fb2f"

    # --- Grammars ---
    grammar_operations(speech_to_text, custom_id, ["list grammars"])
    

if __name__ == '__main__':
    main()
