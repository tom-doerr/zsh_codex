#!/bin/zsh

# This ZSH plugin reads the text from the current buffer 
# and uses a Python script to complete the text.
 

create_completion() {
    # Get the text typed until now.
    text=${BUFFER}
    #echo $cursor_line $cursor_col
    completion=$(echo -n "$text" | $ZSH_CUSTOM/plugins/zsh_codex/create_completion.py $CURSOR)
    text_before_cursor=${text:0:$CURSOR}
    text_after_cursor=${text:$CURSOR}
    # Add completion to the current buffer.
    #BUFFER="${text}${completion}"
    BUFFER="${text_before_cursor}${completion}${text_after_cursor}"
    prefix_and_completion="${text_before_cursor}${completion}"
    # Put the cursor at the end of the completion
    CURSOR=${#prefix_and_completion}
}

# Bind the create_completion function to a key.
zle -N create_completion



