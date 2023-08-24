#!/bin/zsh

# This ZSH plugin reads the text from the current buffer
# and uses a Python script to complete the text.

create_completion() {

  local pipe_path="/tmp/tmp_pipe"

  if [ -p "$pipe_path" ] ; then
      rm -rf "$pipe_path"
  fi
  mkfifo "$pipe_path"

  text=${BUFFER}


  # Run the Python script in the background
  ($ZSH_CUSTOM/plugins/zsh_codex/create_completion.py $text) &
  local python_pid=$!


  # Function to read lines from the named pipe and update the BUFFER
  while true; do
    # Read a line of output from the named pipe
    if read output ;then
      # Update the BUFFER variable with the current output
      BUFFER+=$output
      # Redraw the command line to display the updated BUFFER
      zle -R
    fi

    # Check if the Python script has exited
    if ! kill -0 $python_pid 2>/dev/null; then
      break
    fi
  done <"$pipe_path";

  # Remove Pipe
  rm -rf "$pipe_path"

  # Redraw the command line once more to clear any remaining text
  zle -R
  zle cursor-forward #move cursor to end of BUFFER

  #Find Commands in generated text
  local input=$BUFFER
  substrings=()

  local delimiter="\`\`\`"


  while [[ "$input" == *"$delimiter"* ]]; do
      before_delimiter="${input%%$delimiter*}"
      input="${input#*$delimiter}"

      if [[ "$input" == *"$delimiter"* ]]; then
          substring="${input%%$delimiter*}"
          substrings+=("$substring")
          echo "Substring: $substring"
      fi

      input="${input#*$delimiter}"
  done

  local delimiter="sh\`\`\`"


  while [[ "$input" == *"$delimiter"* ]]; do
      before_delimiter="${input%%$delimiter*}"
      input="${input#*$delimiter}"

      if [[ "$input" == *"$delimiter"* ]]; then
          substring="${input%%$delimiter*}"
          substrings+=("$substring")
          echo "Substring: $substring"
      fi

      input="${input#*$delimiter}"
  done

  substrings=("${substrings[@]:1}")

  #local options=("Apple" "Banana" "Ananas" "Apple" "Banana" "Ananas" "Apple" "Banana" "Ananas" "Apple" "Banana" "Ananas" "Apple" "Banana" "Ananas" "Apple" "Banana" "Ananas")
  _my_custom_completion "${substrings[@]}"
  }

_my_custom_completion() {
  local strings=("$@")             # Store the list of strings passed as arguments
  local selected_index=-1           # Initialize the index of the currently selected string

  _my_custom_display_strings() {
    local selected_string=$1
    local display_text=()
    local current_column=0


    local max_length=0
    local minimal_lenght=20
    for string in "${strings[@]}"; do
      if [[ ${#string} -gt $max_length ]]; then
        max_length=${#string}
      fi
    done

    if [[ $minimal_lenght -gt $max_length ]]; then
      max_length=$minimal_lenght
    fi


    local terminal_columns=$(tput cols)  # Get the number of columns in the terminal
    local max_columns=$((terminal_columns / (max_length + 1)))  # Calculate max_columns

    tput sc       # Save the cursor position
    tput cud1     # Move the cursor down by 1 line
    tput cuf 0    # Move the cursor to the beginning of the line
    tput el       # Clear the line

    local rows=0
    local columns=0
    tput cub1 # Some wiredness required to the first row be alligned with the ohters
    local counter=0

    for string in "${strings[@]}"; do

      if [[ $columns -gt $max_columns-1 ]]; then
        tput cud1  # increase row by 1
        columns=0 # go back to the left
      fi

      tput cuf $((column * (max_length))) #move by one max_lenght to the left
      local padding=$((max_length - ${#string})) #needed to overwirte some wiredness

      if [[ $counter == $selected_string ]]; then
        printf "\033[30;47m%s%${padding}s\033[0m" "$string" "" # highlight selection
      else
        printf "%s%${padding}s" "$string"  # Print with padding


      fi

      tput el

      ((columns++))
      ((counter++))

    done
    tput rc       # Restore the saved cursor position
  }

_my_custom_handle_input() {
  local key
  local selected_index=0
  bindkey -r '^I'

  while read -s -k key; do
    case $key in
      $'\x09')  # Tab key
        if [[ $selected_index -ge ${#strings[@]} ]]; then
          selected_index=0         # Reset index to zero if end is reached
        fi
        _my_custom_display_strings $selected_index
        ((selected_index++))
        ;;
      $'\x0d')  # Enter key
        zle reset-prompt
        BUFFER="${strings[selected_index]}"
        zle -R
        return
        ;;
    esac
  done

  bindkey '^I' expand-or-complete
}


  _my_custom_display_strings $selected_index       # Initial display of the list of strings
  _my_custom_handle_input    # Attach the input handler
}


# Bind the create_completion function to a key.
zle -N create_completion



