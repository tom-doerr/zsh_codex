#!/usr/bin/env python3

import argparse
import sys

from services.services import ClientFactory


def main():
    parser = argparse.ArgumentParser(
        description="Generate command completions using AI."
    )
    parser.add_argument(
        "cursor_position", type=int, help="Cursor position in the input buffer"
    )
    args = parser.parse_args()

    client = ClientFactory.create()

    # Read the input prompt from stdin.
    buffer = sys.stdin.read()
    zsh_prefix = "#!/bin/zsh\n\n"
    buffer_prefix = buffer[: args.cursor_position]
    buffer_suffix = buffer[args.cursor_position :]
    full_command = zsh_prefix + buffer_prefix + buffer_suffix

    completion = client.get_completion(full_command)

    if completion.startswith(zsh_prefix):
        completion = completion[len(zsh_prefix) :]

    line_prefix = buffer_prefix.rsplit("\n", 1)[-1]
    # Handle all the different ways the command can be returned
    for prefix in [buffer_prefix, line_prefix]:
        if completion.startswith(prefix):
            completion = completion[len(prefix) :]
            break

    if buffer_suffix and completion.endswith(buffer_suffix):
        completion = completion[: -len(buffer_suffix)]

    completion = completion.strip("\n")
    if line_prefix.strip().startswith("#"):
        completion = "\n" + completion

    sys.stdout.write(completion)


if __name__ == "__main__":
    main()
