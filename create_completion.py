#!/usr/bin/env python3

import sys
import os
import configparser
import argparse

# Check for required libraries
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

CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
OPENAI_API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')
GEMINI_API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'geminiapirc')
GROQ_API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'groqapirc')

def create_template_ini_file(api_type):
    file_info = {
        'openai': (OPENAI_API_KEYS_LOCATION, '[openai]\nsecret_key=\n', 'https://platform.openai.com/api-keys'),
        'gemini': (GEMINI_API_KEYS_LOCATION, '[gemini]\napi_key=\n', 'Google AI Studio'),
        'groq': (GROQ_API_KEYS_LOCATION, '[groq]\napi_key=\n', 'Groq API dashboard')
    }
    
    file_path, content, url = file_info[api_type]
    
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f'{api_type.capitalize()} API config file created at {file_path}')
        print('Please edit it and add your API key')
        print(f'If you do not yet have an API key, you can get it from: {url}')
        sys.exit(1)

def initialize_api(api_type):
    create_template_ini_file(api_type)
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_DIR, f'{api_type}apirc'))
    api_config = {k: v.strip("\"'") for k, v in config[api_type].items()}
    
    if api_type == 'openai':
        client = OpenAI(
            api_key=api_config["secret_key"],
            base_url=api_config.get("base_url", "https://api.openai.com/v1"),
            organization=api_config.get("organization")
        )
        api_config["model"] = api_config.get("model", "gpt-3.5-turbo-0613")
    elif api_type == 'gemini':
        genai.configure(api_key=api_config["api_key"])
        client = genai
        api_config["model"] = api_config.get("model", "gemini-1.5-pro-latest")
    else:  # groq
        client = Groq(api_key=api_config["api_key"])
        api_config["model"] = api_config.get("model", "llama3-8b-8192")
    
    return client, api_config

def get_completion(api_type, client, config, full_command):
    system_message = "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation. Do not put completed command in a code block."
    
    if api_type == 'openai':
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": 'system', "content": system_message},
                {"role": 'user', "content": full_command},
            ],
            temperature=float(config.get("temperature", 1.0))
        )
        return response.choices[0].message.content
    elif api_type == 'gemini':
        model = client.GenerativeModel(config["model"])
        chat = model.start_chat(history=[])
        prompt = f"{system_message}\n\n{full_command}"
        response = chat.send_message(prompt)
        return response.text
    else:  # groq
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": 'system', "content": system_message},
                {"role": 'user', "content": full_command},
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

    api_libs = {'openai': OpenAI, 'gemini': genai, 'groq': Groq}
    if api_libs[args.api] is None:
        print(f"{args.api.capitalize()} library is not installed. Please install it using 'pip install {args.api}'")
        sys.exit(1)

    client, config = initialize_api(args.api)
    
    buffer = sys.stdin.read()
    zsh_prefix = '#!/bin/zsh\n\n'
    buffer_prefix = buffer[:args.cursor_position]
    buffer_suffix = buffer[args.cursor_position:]
    full_command = f"{zsh_prefix}{buffer_prefix}{buffer_suffix}"

    completion = get_completion(args.api, client, config, full_command)

    if completion.startswith(zsh_prefix):
        completion = completion[len(zsh_prefix):]

    line_prefix = buffer_prefix.rsplit("\n", 1)[-1]
    for prefix in [buffer_prefix, line_prefix]:
        if completion.startswith(prefix):
            completion = completion[len(prefix):]
            break

    completion = completion.rstrip(buffer_suffix).strip("\n")
    if line_prefix.strip().startswith("#"):
        completion = f"\n{completion}"

    sys.stdout.write(completion)

if __name__ == "__main__":
    main()
