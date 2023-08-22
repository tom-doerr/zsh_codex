#!/bin/zsh

# This ZSH plugin reads the text from the current buffer 
# and uses a Python script to complete the text.

create_completion() {

    local pipe_path="/tmp/tmp_pipe"
    [ ! -p "$pipe_path" ] && mkfifo "$pipe_path"

     text=${BUFFER}


  # Run the Python script in the background
  ($ZSH_CUSTOM/plugins/zsh_codex/create_completion.py $text) &
  local python_pid=$!


  # Function to read lines from the named pipe and update the BUFFER
  while true; do
    # Read a line of output from the named pipe
    local output
    if read output < "$pipe_path"; then
      # Update the BUFFER variable with the current output
      BUFFER=$output
      # Redraw the command line to display the updated BUFFER
      zle -R
    fi

    # Check if the Python script has exited
    if ! kill -0 $python_pid 2>/dev/null; then
      break
    fi
  done

  # Wait for the Python script to finish
  wait $python_pid
  rm -f "$pipe_path"

  # Redraw the command line once more to clear any remaining text
  zle -R
  }


# Bind the create_completion function to a key.
zle -N create_completion



