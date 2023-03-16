#!/bin/bash

if [[ -z "$IRR_DB" || -z "$IRR_SERIALHASH" || -z "$IRR_DB_FOLDER" || -z "$IRR_JSON" || -z "$IRR_GOB" ]]; then
    echo "Must define environment variables" 1>&2
    exit 1
fi

# use cli argument $1, if not set fall back to env variable INTERVAL, if not set fall back to default 600
if [[ -z "$1" ]]; then
    int=${INTERVAL:-600}
else
    int=$1
fi

# get containing folder
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

while true
do
	echo ""
    date
    $dir/irrdownload.py $IRR_DB $IRR_SERIALHASH $IRR_DB_FOLDER
    exec 5>&1
    IRR2JSON_OUTPUT=$($dir/irr2json.py $IRR_DB $IRR_SERIALHASH $IRR_JSON | tee >(cat - >&5))
    if grep -qv "nothing" <<< "$(echo $IRR2JSON_OUTPUT | tail -1)"; then
        $dir/convertroas -input $IRR_JSON -output $IRR_GOB
    fi
    echo "Sleeping for $int seconds..."
	sleep $int
done