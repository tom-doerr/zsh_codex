#!/usr/bin/env python3

from llmhub.client import Client as LLMHubClient
import sys
import os
import configparser

LLM = LLMHubClient("https://www.llmhub.com/2/functions/34/share")

cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]

response = LLM.run({"prefix": prompt_prefix,
                    "suffix": prompt_suffix,})

completion_all = response["output"]
completion_list = completion_all.split('\n')
if completion_all[:2] == '\n\n':
    print(completion_all)
elif completion_list[0]:
    print(completion_list[0])
elif len(completion_list) == 1:
    print('')
else:
    print('\n' + completion_list[1])
