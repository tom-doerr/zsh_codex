#!/usr/bin/env python3

from openai import OpenAI
import sys
import os
import configparser

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
            f.write('model=gpt-3.5-turbo-0613\n')

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

    api_key = config['openai']['secret_key'].strip('"').strip("'")
    model_name = config['openai'].get('model', 'gpt-3.5-turbo').strip('"').strip("'")
    client = OpenAI(api_key=api_key)
    return client, model_name

client, model_name = initialize_openai_api()
cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
zsh_prefix = '#!/bin/zsh\n\n'
buffer_prefix = buffer[:cursor_position_char]
buffer_suffix = buffer[cursor_position_char:]
full_command = zsh_prefix + buffer_prefix + buffer_suffix
response = client.chat.completions.create(model=model_name, messages=[
    {
        "role":'system',
        "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation",
    },
    {
        "role":'user',
        "content": full_command,
    }
])
completion: str = response.choices[0].message.content
if completion.startswith(zsh_prefix):
    completion = completion[len(zsh_prefix):]

line_prefix = buffer_prefix.rsplit("\n", 1)[-1]
# Handle all the different ways the command can be returned
for prefix in [buffer_prefix, line_prefix]:
    if completion.startswith(prefix):
        completion = completion[len(prefix):]
        break

if buffer_suffix and completion.endswith(buffer_suffix):
    completion = completion[:-len(buffer_suffix)]

completion = completion.strip("\n")
if line_prefix.strip().startswith("#"):
    completion = "\n" + completion

sys.stdout.write(completion)
