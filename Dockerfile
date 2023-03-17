FROM python:3-alpine

ENV IRR_CACHE_FOLDER=/opt/cache
ENV IRR_DB=$IRR_CACHE_FOLDER/irr.db
ENV IRR_SERIALHASH=$IRR_CACHE_FOLDER/IRR.SERIALHASH
ENV IRR_DB_FOLDER=$IRR_CACHE_FOLDER/dbs
ENV IRR_JSON=$IRR_CACHE_FOLDER/irr.json
ENV IRR_GOB=$IRR_CACHE_FOLDER/irr.gob
ENV INTERVAL=600

RUN apk --no-cache add bash

COPY irrdownload.py irr2json.py loop.sh convertroas /opt/

RUN chmod +x /opt/convertroas

ENTRYPOINT ["/opt/loop.sh"]
