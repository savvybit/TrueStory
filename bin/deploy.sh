#! /usr/bin/env bash


versions="master,develop"

version=$1
if [[ -z "$version" ]]; then
    echo "[x] You must supply a version."
    exit 1
elif [[ ! ",$versions," == *",$version,"* ]]; then
    echo "[x] The version must be one of '$versions'."
    exit 2
fi

if [[ $version == "master" ]]; then
    promote_flag="--promote"
else
    promote_flag="--no-promote"
fi

gcloud app deploy *.yaml -v $version $promote_flag
