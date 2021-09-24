#!/usr/bin/env python3

import openai
import sys
import os
import json

STREAM = False


# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openai_api_keys.json')

# Read the organization_id and secret_key from ~/.config/openai_api_keys.json.
# API_KEYS_LOCATION=os.path.expanduser('~/.config/openai_api_keys.json')

try:
    with open(API_KEYS_LOCATION) as f:
        API_KEYS = json.load(f)
    ORGANIZATION_ID = API_KEYS['ORGANIZATION_ID']
    SECRET_KEY = API_KEYS['SECRET_KEY']
except FileNotFoundError:
    sys.exit('Please create a file called openai_api_keys.json in ~/.config with your ORGANIZATION_ID and SECRET_KEY.')


openai.organization = ORGANIZATION_ID
openai.api_key = SECRET_KEY

# Read the input prompt from stdin.
input_prompt = '#!/bin/zsh\n\n' + sys.stdin.read()


response = openai.Completion.create(engine='davinci-codex', prompt=input_prompt, temperature=0.5, max_tokens=16, stream=STREAM)
# completion = response['choices'][0]['text']
if STREAM:
    while True:
        next_response = next(response)
        print("next_response:", next_response)
        # next_response['choices'][0]['finish_reason']
        print("        next_response['choices'][0]['finish_reason']:",         next_response['choices'][0]['finish_reason'])
        completion = next_response['choices'][0]['text']
        print("completion:", completion)
        # print(next(response))
else:
    completion_all = response['choices'][0]['text']
    completion_list = completion_all.split('\n')
    if completion_list[0]:
        print(completion_list[0])
    elif len(completion_list) == 1:
        print('')
    else:
        print('\n' + completion_list[1])



