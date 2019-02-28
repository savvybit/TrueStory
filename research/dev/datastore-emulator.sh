#! /usr/bin/env bash


path=~/Work/TrueStory

# Open local Datastore emulator.
process=$(ps aux | grep -i datastore | grep -i java | awk '{print $2}')
if [[ ! -z "$process" ]]; then
    echo "[!] Killing active emulator first..."
    kill -9 $process
fi
gcloud beta emulators datastore start --data-dir $path &
echo "[i] Sleeping until emulator is completely initialized..."
while [[ ! -f $path/env.yaml ]]
do
    sleep 1
done
echo "[i] Emulator initialization done; loading env vars..."
$(gcloud beta emulators datastore env-init --data-dir $path)
