## What is it?

This is a ZSH plugin that uses OpenAI Codex to complete text.

## How do I install it?

1. Download the ZSH plugin.

```
    $ git clone https://github.com/tomnomnom/zsh_codex.git ~/.oh-my-zsh/plugins/ 
```

2. Add the following to your `.zshrc` file.

```
    plugins=(zsh_codex)
    bindkey '^X' create_completion
```

3. Create a file called `openaiapirc` in `~/.config` with your ORGANIZATION_ID and SECRET_KEY.

```
[openai]
organization_id = ...
secret_key = ...
```

4. Run `zsh`, start typing and complete it using `^X`!
