#!/usr/bin/env python3

import asyncio
import openai
import sys
import os
import configparser
import platform
import functools
import subprocess

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


@functools.lru_cache(maxsize=None)
async def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')
            f.write('model=gpt-4-0314\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
              'need to register for OpenAI Codex: \n'
              'https://openai.com/blog/openai-codex/')
        sys.exit(1)


@functools.lru_cache(maxsize=None)
async def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    await create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")

    if 'model' in config['openai']:
        model = config['openai']['model'].strip('"').strip("'")
    else:
        model = 'gpt-4'

    return model


# model = initialize_openai_api()
model = asyncio.run(initialize_openai_api())

cursor_position_char = int(sys.argv[1])


@functools.lru_cache(maxsize=None)
async def get_system_info():
    """
    Gather system information
    """
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor()
    }
    return system_info


system_info = asyncio.run(get_system_info())


@functools.lru_cache(maxsize=None)
async def get_installed_packages():
    # Get list of installed packages
    try:
        if system_info['os'] == 'Linux':
            installed_packages = subprocess.check_output(['dpkg', '--get-selections']).decode('utf-8')
        elif system_info['os'] == 'Darwin':
            installed_packages = subprocess.check_output(['brew', 'list']).decode('utf-8')
        else:
            installed_packages = "Unsupported OS for package listing"
    except Exception as e:
        installed_packages = f"Error getting installed packages: {str(e)}"
    return installed_packages


installed_packages = asyncio.run(get_installed_packages())

# Get current working directory
current_directory = os.getcwd()
# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix
response = openai.ChatCompletion.create(model=model, messages=[
    {
        "role": 'system',
        "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation",
    },
    {
        "role": 'user',
        "content": f"I'm using a {system_info['os']} system with version {system_info['os_version']} on a {system_info['architecture']} architecture with a {system_info['processor']} processor. The current directory is {current_directory}. Here are some of my installed packages:\n{installed_packages}",
    },
    {
        "role": 'user',
        "content": full_command,
    }
])
completed_command = response['choices'][0]['message']['content']

sys.stdout.write(f"\n{completed_command}")
