FROM python:3-alpine

ENV IRR_CACHE_FOLDER=/opt/cache
ENV IRR_DB=$IRR_CACHE_FOLDER/irr.db
ENV IRR_SERIALHASH=$IRR_CACHE_FOLDER/IRR.SERIALHASH
ENV IRR_DB_FOLDER=$IRR_CACHE_FOLDER/dbs
ENV IRR_JSON=$IRR_CACHE_FOLDER/irr.json
ENV INTERVAL=600

COPY irrdownload.py irr2json.py loop.sh /opt/

#ENTRYPOINT ["/usr/bin/bash", "/opt/loop.sh"]
ENTRYPOINT ["/bin/sh", "/opt/loop.sh"]
