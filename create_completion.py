#!/usr/bin/env python3

import os
import json
import subprocess
import sys

conf = None
home_directory = os.path.expanduser( '~' )
with open(home_directory+'/.oh-my-zsh/custom/plugins/zsh_codex/config.json') as f:
    conf = json.load(f)

top_k = conf["top_k"]
top_p = conf["top_p"]
temp = conf["temp"]
n = conf["n"]
main = conf["path_to_starcoder.cpp"] +"main"
model = conf["path_to_starcoder.cpp"] + conf["model_name"]
system = "<|system|> You are a linux shell expert, please help me complete the following command in the most efficient and shortest way possible. Start your reponse by giving a least detailed step by step explanation for all parts of the shell command. End you response with the completed command. <|end|>:"
params = f"--top_k {top_k} --top_p {top_p} --temp {temp} -n {n}"


text = str(sys.argv[1])
query= main + ' -m ' + model + ' -p \"' + system + " " + text + " \" " + params

pipe_path = "/tmp/tmp_pipe"
log = home_directory+'/.oh-my-zsh/custom/plugins/zsh_codex/info.log'

with open(pipe_path, 'w') as pipe, open(log, 'w') as log:
    log.write(f"------------Query------------ {query} \n ------------Outputs------------\n")
    process = subprocess.Popen(query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    with process.stdout:
        for line in iter(process.stdout.readline, ''):
            log.write(line)
            pipe.write(line)
            pipe.flush()
