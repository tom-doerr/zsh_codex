import os
import json
import sys

conf = None
with open('config.json') as f:
    conf = json.load(f)

top_k = conf["top_k"]
top_p = conf["top_p"]
temp = conf["temp"]
n = conf["n"]
main = conf["path_to_starcoder_cpp_main"]
model = conf["model_name"]
system = "<|system|> You are a linux shell expert, please help me complete the following command in the most efficient and shortest way possible. Start your reponse by giving a least detailed step by step explanation for all parts of the shell command. End you response with the completed command. <|end|>:"
params = f"--top_k {top_k} --top_p {top_p} --temp {temp} -n {n}"


cursor_position_char = int(sys.argv[1])
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix
querry= main + ' -m ' + model + ' -p \"' + system + " " + full_command + " \" " + params

stream = os.popen(querry)
output = stream.read()
sys.stdout.write(f"\n{output}")
