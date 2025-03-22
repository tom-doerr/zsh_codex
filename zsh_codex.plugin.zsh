#!/bin/zsh

# This ZSH plugin reads the text from the current buffer
# and uses a Python script to complete the text.
api="openai"

_ZSH_CODEX_REPO=$(dirname $0)

create_completion() {
    # Get the text typed until now.
    local text=$BUFFER
    if [[ "$ZSH_CODEX_PREEXECUTE_COMMENT" == "true" ]]; then
        text="$(echo -n "echo \"$text\"" | zsh)"
    fi
    local ZSH_CODEX_PYTHON="${ZSH_CODEX_PYTHON:-python3}"
    local completion=$(echo -n "$text" | $ZSH_CODEX_PYTHON $_ZSH_CODEX_REPO/create_completion.py $CURSOR)
    local text_before_cursor=${BUFFER:0:$CURSOR}
    local text_after_cursor=${BUFFER:$CURSOR}

    # Add completion to the current buffer.
    BUFFER="${text_before_cursor}${completion}${text_after_cursor}"

    # Put the cursor at the end of the completion
    CURSOR=$((CURSOR + ${#completion}))
}

# Bind the create_completion function to a key.
zle -N create_completion
# You may want to add a key binding here, e.g.:
# bindkey '^X^E' create_completion
