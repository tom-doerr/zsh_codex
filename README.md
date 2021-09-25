<h1 align="center">⌨️ 🦾 Zsh Codex</h1>

<p align="center">
    AI in the commandline.
</p>

<p align="center">
    <a href="https://github.com/tom-doerr/zsh_codex/stargazers"
        ><img
            src="https://img.shields.io/github/stars/tom-doerr/zsh_codex"
            alt="Repository's starts"
    /></a>
    <a href="https://github.com/tom-doerr/zsh_codex/issues"
        ><img
            src="https://img.shields.io/github/issues-raw/tom-doerr/zsh_codex"
            alt="Issues"
    /></a>
    <a href="https://github.com/tom-doerr/zsh_codex/blob/main/LICENSE"
        ><img
            src="https://img.shields.io/github/license/tom-doerr/zsh_codex"
            alt="License"
    /><br />
    <a href="https://github.com/tom-doerr/zsh_codex/commits/main"
		><img
			src="https://img.shields.io/github/last-commit/tom-doerr/zsh_codex/main"
			alt="Latest commit"
    /></a>
    <a href="https://github.com/tom-doerr/zsh_codex"
        ><img
            src="https://img.shields.io/github/repo-size/tom-doerr/zsh_codex"
            alt="GitHub repository size"
    /></a>
</p>

<p align="center">
    <img src='https://github.com/tom-doerr/bins/raw/main/zsh_codex/zc3.gif'>
</p>

## What is it?

This is a ZSH plugin that uses OpenAI Codex to complete text.

## How do I install it?

1. Download the ZSH plugin.

```
    $ git clone https://github.com/tom-doerr/zsh_codex.git ~/.oh-my-zsh/plugins/ 
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
