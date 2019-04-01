#! /usr/bin/env bash


# Working path for the entire data of the developed app.
path=~/Work/TrueStory
mkdir -p $path
echo "[i] Saving app data under '$path'."

if [[ $1 == "gae" ]]; then
    echo "[i] Starting server with GAE."
    dev_appserver.py . -A truestory --log_level debug --storage_path $path \
    --enable_console --support_datastore_emulator False
else
    echo "[i] Installing requirements..."
    pip3 install -Ur requirements-dev.txt
    pip3 install -e .
    echo "[i] Starting server with Flask."
    FLASK_APP=truestory FLASK_ENV=development flask run -p 8080
fi
