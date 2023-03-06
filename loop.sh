#!/bin/bash

if [[ -z "$IRR_DB" || -z "$IRR_SERIALHASH" || -z "$IRR_DB_FOLDER" || -z "$IRR_JSON" ]]; then
    echo "Must define environment variables" 1>&2
    exit 1
fi

# use cli argument $1, if not set fall back to env variable INTERVAL, if not set fall back to default 600
if [[ -z "$1" ]]; then
    INT=${INTERVAL:-600}
else
    INT=$1
fi

while true
do
	./irrdownload.py $IRR_DB $IRR_SERIALHASH $IRR_DB_FOLDER
    ./irr2json.py $IRR_DB $IRR_SERIALHASH $IRR_JSON
	sleep $INT
done