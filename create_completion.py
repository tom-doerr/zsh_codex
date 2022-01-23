#!/usr/bin/env python3

import openai
import sys
import os
import configparser

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
        print('If you do not yet have an organization ID and secret key, you\n'
               'need to register for OpenAI Codex: \n'
                'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")


initialize_openai_api()

# Read the input prompt from stdin.
input_prompt = '#!/bin/zsh\n\n' + sys.stdin.read()


response = openai.Completion.create(engine='code-davinci-001', prompt=input_prompt, temperature=0.5, max_tokens=50, stream=STREAM)
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



