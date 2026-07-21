#!/bin/bash

gcloud config set project agents-cli-503022
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
echo $GOOGLE_CLOUD_PROJECT