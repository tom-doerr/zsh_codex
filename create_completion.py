#!/usr/bin/env python3

import asyncio
import openai
import sys
import os
import configparser
import platform
import subprocess
import json
import time


# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')


CACHE_DIR = os.path.join(CONFIG_DIR, 'cache/zsh_codex')
os.makedirs(CACHE_DIR, exist_ok=True)
SYSTEM_INFO_CACHE_FILE = os.path.join(CACHE_DIR, 'system_info.json')
INSTALLED_PACKAGES_CACHE_FILE = os.path.join(CACHE_DIR, 'installed_packages.json')
CACHE_EXPIRATION_TIME = 60 * 60 * 24  # 24 hours







def load_or_save_to_cache(filename, default_func):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        if time.time() - data['timestamp'] < CACHE_EXPIRATION_TIME:
            return data['value']

    data = {
        'value': default_func(),
        'timestamp': time.time()
    }
    with open(filename, 'w') as f:
        json.dump(data, f)

    return data['value']

# Read the organization_id and secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<your organization ID>
# secret_key=<your secret key>

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations

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


async def get_system_info():
    """
    Gather system information
    """

    def default_func():
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor()
        }

    return load_or_save_to_cache(SYSTEM_INFO_CACHE_FILE, default_func)


system_info = asyncio.run(get_system_info())


# last ten recent packages
async def get_installed_packages():
    # Get list of installed packages
    def default_func():
        try:
            if system_info['os'] == 'Linux':
                command = "dpkg --get-selections | head -n 10"
                return subprocess.check_output(command, shell=True).decode('utf-8')
            elif system_info['os'] == 'Darwin':
                command = "brew list -1t 2> /dev/null | head -n 10"
                return subprocess.check_output(command, shell=True).decode('utf-8')
            else:
                return "Unsupported OS for package listing"
        except subprocess.CalledProcessError as e:
            return f"Error getting installed packages: {str(e)}"

    return load_or_save_to_cache(INSTALLED_PACKAGES_CACHE_FILE, default_func)

    

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
