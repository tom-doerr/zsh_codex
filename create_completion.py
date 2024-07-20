#!/usr/bin/env python3

import sys
import os
import configparser
import argparse

# Conditionally import OpenAI, Google Generative AI, and Groq
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from groq import Groq
except ImportError:
    Groq = None

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
OPENAI_API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')
GEMINI_API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'geminiapirc')
GROQ_API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'groqapirc')

def create_template_ini_file(api_type):
    """
    If the ini file does not exist create it and add the api_key placeholder
    """
    if api_type == 'openai':
        file_path = OPENAI_API_KEYS_LOCATION
        content = '[openai]\nsecret_key=\n'
        url = 'https://platform.openai.com/api-keys'
    elif api_type == 'gemini':
        file_path = GEMINI_API_KEYS_LOCATION
        content = '[gemini]\napi_key=\n'
        url = 'Google AI Studio'
    else:  # groq
        file_path = GROQ_API_KEYS_LOCATION
        content = '[groq]\napi_key=\n'
        url = 'Groq API dashboard'

    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write(content)

        print(f'{api_type.capitalize()} API config file created at {file_path}')
        print('Please edit it and add your API key')
        print(f'If you do not yet have an API key, you can get it from: {url}')
        sys.exit(1)

def initialize_api(api_type):
    """
    Initialize the specified API
    """
    create_template_ini_file(api_type)
    config = configparser.ConfigParser()
    
    if api_type == 'openai':
        config.read(OPENAI_API_KEYS_LOCATION)
        api_config = {k: v.strip("\"'") for k, v in config["openai"].items()}
        client = OpenAI(
            api_key=api_config["secret_key"],
            base_url=api_config.get("base_url", "https://api.openai.com/v1"),
            organization=api_config.get("organization")
        )
        api_config.setdefault("model", "gpt-3.5-turbo-0613")
        return client, api_config
    elif api_type == 'gemini':
        config.read(GEMINI_API_KEYS_LOCATION)
        api_config = {k: v.strip("\"'") for k, v in config["gemini"].items()}
        genai.configure(api_key=api_config["api_key"])
        api_config.setdefault("model", "gemini-1.5-pro-latest")
        return genai, api_config
    else:  # groq
        config.read(GROQ_API_KEYS_LOCATION)
        api_config = {k: v.strip("\"'") for k, v in config["groq"].items()}
        client = Groq(api_key=api_config["api_key"])
        api_config.setdefault("model", "llama3-8b-8192")
        return client, api_config

def get_completion(api_type, client, config, full_command):
    if api_type == 'openai':
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {
                    "role": 'system',
                    "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation. Do not put completed command in a code block.",
                },
                {
                    "role": 'user',
                    "content": full_command,
                }
            ],
            temperature=float(config.get("temperature", 1.0))
        )
        return response.choices[0].message.content
    elif api_type == 'gemini':
        model = client.GenerativeModel(config["model"])
        chat = model.start_chat(history=[])
        prompt = "You are a zsh shell expert, please help me complete the following command. Only output the completed command, no need for any other explanation. Do not put the completed command in a code block.\n\n" + full_command
        response = chat.send_message(prompt)
        return response.text
    else:  # groq
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {
                    "role": 'system',
                    "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation. Do not put completed command in a code block.",
                },
                {
                    "role": 'user',
                    "content": full_command,
                }
            ],
            temperature=float(config.get("temperature", 0.5)),
            max_tokens=int(config.get("max_tokens", 1024)),
            top_p=float(config.get("top_p", 0.65)),
            stream=False,
        )
        return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="Generate command completions using AI.")
    parser.add_argument('--api', choices=['openai', 'gemini', 'groq'], default='openai', help="Choose the API to use (default: openai)")
    parser.add_argument('cursor_position', type=int, help="Cursor position in the input buffer")
    args = parser.parse_args()

    if args.api == 'openai' and OpenAI is None:
        print("OpenAI library is not installed. Please install it using 'pip install openai'")
        sys.exit(1)
    elif args.api == 'gemini' and genai is None:
        print("Google Generative AI library is not installed. Please install it using 'pip install google-generativeai'")
        sys.exit(1)
    elif args.api == 'groq' and Groq is None:
        print("Groq library is not installed. Please install it using 'pip install groq'")
        sys.exit(1)

    client, config = initialize_api(args.api)
    
    # Read the input prompt from stdin.
    buffer = sys.stdin.read()
    zsh_prefix = '#!/bin/zsh\n\n'
    buffer_prefix = buffer[:args.cursor_position]
    buffer_suffix = buffer[args.cursor_position:]
    full_command = zsh_prefix + buffer_prefix + buffer_suffix

    completion = get_completion(args.api, client, config, full_command)

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

if __name__ == "__main__":
    main()