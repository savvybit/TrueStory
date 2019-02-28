#! /usr/bin/env bash


# Working path for the app.
path=~/Work/TrueStory
mkdir -p $path
echo "[i] Saving app data under '$path'."

echo "[i] Starting app server..."
dev_appserver.py . -A truestory --log_level debug --storage_path $path --enable_console \
    --support_datastore_emulator False
