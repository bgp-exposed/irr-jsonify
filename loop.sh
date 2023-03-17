#!/bin/bash
irr_cache_folder=${IRR_CACHE_FOLDER:-./cache}
irr_db=${IRR_DB:-$irr_cache_folder/irr.db}
irr_serialhash=${IRR_SERIALHASH:-$irr_cache_folder/IRR.SERIALHASH}
irr_db_folder=${IRR_DB_FOLDER:-$irr_cache_folder/dbs}
irr_json=${IRR_JSON:-$irr_cache_folder/irr.json}
irr_gob=${IRR_GOB:-$irr_cache_folder/irr.gob}

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
    $dir/irrdownload.py $irr_db $irr_serialhash $irr_db_folder
    exec 5>&1
    IRR2JSON_OUTPUT=$($dir/irr2json.py $irr_db $irr_serialhash $irr_json | tee >(cat - >&5))
    if grep -qv "nothing" <<< "$(echo $IRR2JSON_OUTPUT | tail -1)"; then
        $dir/convertroas -input $irr_json -output $irr_gob
    fi
    echo "Sleeping for $int seconds..."
	sleep $int
done