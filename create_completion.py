#!/usr/bin/env python3

from openai import OpenAI
import sys
import os
import configparser

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')
# Read the configuration from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# secret_key=<your secret key>
# organization=<your organization ID>
# model=<model to use>
# temperature=<temperature to use for generations>

def create_template_ini_file():
    """
    If the ini file does not exist create it and add the secret_key placeholder
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('secret_key=\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your secret key')
        print('If you do not yet have a secret key, you can get it at: https://platform.openai.com/api-keys')
        print('You can also optionally add model, organization and temperature')
        sys.exit(1)


def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    config = {k: v.strip("'\"") for k, v in config["openai"].items()}
    assert "secret_key" in config, "Can't find secret_key in config"
    client = OpenAI(api_key=config["secret_key"], organization=config.get("organization"))
    return client, config

client, config = initialize_openai_api()
cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix
response = client.chat.completions.create(
    model=config["model"],
    messages=[
        {
            "role":'system',
            "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation",
        },
        {
            "role":'user',
            "content": full_command,
        }
    ],
    temperature=float(config["temperature"])
)
completed_command = response.choices[0].message.content
if prompt_prefix in completed_command:
    completion = completed_command.replace(prompt_prefix, '', 1)
else:
    # Handle the case when output misses #!/bin/zsh
    completion = completed_command.replace(buffer[:cursor_position_char], "", 1)
completion = completion.replace(prompt_suffix, "", 1)

if buffer.strip().startswith("#"):
    completion = "\n" + completion

sys.stdout.write(completion)
