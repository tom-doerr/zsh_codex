#!/usr/bin/env python3

import openai
import sys
import os

STREAM = False


# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

# Read the organization_id and secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<your organization ID>
# secret_key=<your secret key>

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations


def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        sys.exit(1)


try:
    with open(API_KEYS_LOCATION) as f:
        config = f.read()

    config = '\n' + config 
    # Reading the values works even when there are spaces around the = sign.
    organization_id = config.split('organization_id')[1].split('=')[1].split('\n')[0].strip()
    secret_key = config.split('secret_key')[1].split('=')[1].split('\n')[0].strip()
except:
    print("Unable to read openaiapirc at {}".format(API_KEYS_LOCATION))
    create_template_ini_file()


# Remove the quotes if there are any.
if organization_id[0] == '"' and organization_id[-1] == '"':
    organization_id = organization_id[1:-1]

if secret_key[0] == '"' and secret_key[-1] == '"':
    secret_key = secret_key[1:-1]

openai.api_key = secret_key
openai.organization = organization_id

# Read the input prompt from stdin.
input_prompt = '#!/bin/zsh\n\n' + sys.stdin.read()


response = openai.Completion.create(engine='davinci-codex', prompt=input_prompt, temperature=0.5, max_tokens=32, stream=STREAM)
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
    if completion_all[:2] == '\n\n':
        print(completion_all)
    elif completion_list[0]:
        print(completion_list[0])
    elif len(completion_list) == 1:
        print('')
    else:
        print('\n' + completion_list[1])



