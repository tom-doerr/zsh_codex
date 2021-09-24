#!/bin/zsh

# This ZSH plugin reads the text from the current buffer 
# and uses a Python script to complete the text.
 

create_completion() {
    # Get the text typed until now.
    text=${BUFFER}
    # Write the current timestamp to the file /home/tom/git/zsh_codex/test.txt
    echo $(date +"%T") >> /home/tom/git/zsh_codex/test.txt
    completion=$(printf "$text" | ./create_completion.py)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

# Bind the create_completion function to a key.
zle -N create_completion
bindkey '^X' create_completion



