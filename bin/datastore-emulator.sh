#! /usr/bin/env bash


# Closing existing Datastore emulator if any.
process=$(ps aux | grep -i datastore | grep -i java | awk '{print $2}')
if [[ ! -z "$process" ]]; then
    echo "[!] Killing active emulator first..."
    kill -9 $process
fi
rm -f $DATASTORE_ENV_YAML

# Open new local Datastore emulator.
gcloud beta emulators datastore start --data-dir $WORK_PATH &
echo "[i] Sleeping until emulator is completely initialized..."
while [[ ! -f $DATASTORE_ENV_YAML ]]
do
    sleep 1
done
echo "[i] Emulator initialization done; loading env vars..."
$(gcloud beta emulators datastore env-init --data-dir $WORK_PATH)
