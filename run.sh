#! /usr/bin/env bash


# Working path for the entire data of the developed app.
path=~/Work/TrueStory
mkdir -p $path
echo "[i] Saving app data under '$path'."

if [[ $1 == "gae" ]]; then
    echo "[i] Starting server with GAE."
    dev_appserver.py . -A truestory --log_level debug --storage_path $path \
        --enable_console --support_datastore_emulator True \
        --datastore_emulator_port 8081 --env_var DATASTORE_EMULATOR_HOST=localhost:8081
else
    echo "[i] Installing requirements..."
    pip3 install -Ur requirements-dev.txt
    pip3 install -e .
    echo "[i] Starting server with Flask."
    FLASK_APP=truestory FLASK_ENV=development flask run -p 8080
fi
