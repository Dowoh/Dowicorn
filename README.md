# DiscordBot

## Prerequisites

python >= 3.11
pip

## How to setup

`pip install -r requirements.txt`

To update the requierements.txt => pipreqs . --force


python -m pipx runpip pipreqs install  # ensures pipreqs is installed in pipx env
pipx run pipreqs . --force --ignore venv

## How to run in development mode

`python main.py`

or

`$env:ENV_FOR_DYNACONF="DEVELOPMENT"; python main.py`

## How to run in production mode

` ENV_FOR_DYNACONF=production python main.py `   Linux
` $env:ENV_FOR_DYNACONF="production"; python main.py `  VSC

# To launch in linux and be able to quit without stopping the program, you can use tmux

# "tmux attach" to go back to the screen

# to close tmux session, just do "ctrl+b" and then "d"


Je peux ajouter qu'il ne peuvent pas faire de 10man ou etre seulement dans les raid avec les template 20man

Après, faire qu'après un certain nombre de raid, ils perdent le role, yep c'est possible
