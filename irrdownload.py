#!/usr/bin/env python3

from threading import Thread
import urllib.request as request
import os
import zlib
import re
import hashlib
import sys

if len(sys.argv) != 4:
    print("Usage:\nirrdownload.py <irr.db> <IRR.SERIALHASH> <db_folder>")
    exit(1)

export_file = sys.argv[1]
serial_hash_file = sys.argv[2]
db_folder = sys.argv[3]

irr_sources = [
    ["ftp://irr.bboi.net/bboi.db.gz", "ftp://irr.bboi.net/BBOI.CURRENTSERIAL"],
    ["ftp://rr.Level3.net/pub/rr/level3.db.gz", "ftp://rr.level3.net/pub/rr/LEVEL3.CURRENTSERIAL"],
    ["https://ftp.lacnic.net/lacnic/irr/lacnic.db.gz", "https://ftp.lacnic.net/lacnic/irr/LACNIC.CURRENTSERIAL"],
    ["https://ftp.ripe.net/ripe/dbase/split/ripe.db.route6.gz", "https://ftp.ripe.net/ripe/dbase/RIPE.CURRENTSERIAL"],
    ["https://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz", "https://ftp.ripe.net/ripe/dbase/RIPE.CURRENTSERIAL"],
    ["ftp://ftp.apnic.net/pub/apnic/whois/apnic.db.route6.gz", "ftp://ftp.apnic.net/pub/apnic/whois/APNIC.CURRENTSERIAL"],
    ["ftp://ftp.apnic.net/pub/apnic/whois/apnic.db.route.gz", "ftp://ftp.apnic.net/pub/apnic/whois/APNIC.CURRENTSERIAL"],
    ["ftp://ftp.radb.net/radb/dbase/radb.db.gz", "ftp://ftp.radb.net/radb/dbase/RADB.CURRENTSERIAL"],
    ["http://ftp.afrinic.net/pub/dbase/afrinic.db.gz", "http://ftp.afrinic.net/pub/dbase/AFRINIC.CURRENTSERIAL"],
    ["ftp://ftp.radb.net/radb/dbase/arin.db.gz", "ftp://ftp.radb.net/radb/dbase/ARIN.CURRENTSERIAL"],
    ["ftp://ftp.altdb.net/pub/altdb/altdb.db.gz", "ftp://ftp.altdb.net/pub/altdb/ALTDB.CURRENTSERIAL"],
    ["ftp://ftp.radb.net/radb/dbase/bell.db.gz", "ftp://ftp.radb.net/radb/dbase/BELL.CURRENTSERIAL"],
    ["ftp://ftp.radb.net/radb/dbase/canarie.db.gz", "ftp://ftp.radb.net/radb/dbase/CANARIE.CURRENTSERIAL"],
    ["ftp://irr-mirror.idnic.net/idnic.db.gz", "ftp://irr-mirror.idnic.net/IDNIC.CURRENTSERIAL"],
    ["ftp://ftp.nic.ad.jp/jpirr/jpirr.db.gz", "ftp://ftp.nic.ad.jp/jpirr/JPIRR.CURRENTSERIAL"],
    ["ftp://rr1.ntt.net/nttcomRR/nttcom.db.gz", "ftp://rr1.ntt.net/nttcomRR/NTTCOM.CURRENTSERIAL"],
    ["ftp://ftp.panix.com/pub/rrdb/panix.db.gz", "ftp://ftp.panix.com/pub/rrdb/PANIX.CURRENTSERIAL"],
    ["ftp://ftp.ripe.net/ripe/dbase/split/ripe-nonauth.db.route6.gz", "ftp://ftp.ripe.net/ripe/dbase/RIPE-NONAUTH.CURRENTSERIAL"],
    ["ftp://ftp.ripe.net/ripe/dbase/split/ripe-nonauth.db.route.gz", "ftp://ftp.ripe.net/ripe/dbase/RIPE-NONAUTH.CURRENTSERIAL"],
    ["ftp://ftp.bgp.net.br/tc.db.gz", "ftp://ftp.bgp.net.br/TC.CURRENTSERIAL"]
]

rx = re.compile(r"\.gz(ip)?$", re.IGNORECASE)

irr_dbs = []
irr_serials = []

if not os.path.exists(db_folder):
    os.mkdir(db_folder)


def download(irr_source, irr_current_serial):
    gz_filename = irr_source.split("/")[-1]
    filename = rx.sub("", gz_filename)
    serial_filename = rx.sub("", irr_current_serial.split("/")[-1])
    current_serial_req = request.urlopen(irr_current_serial)
    current_serial = int(current_serial_req.read())

    update = False
    f_serial = None
    file_serial = "0"
    if os.path.isfile(f"{db_folder}/{serial_filename}") and os.path.isfile(f"{db_folder}/{filename}"):
        f_serial = open(f"{db_folder}/{serial_filename}", "r+")
        file_serial = f_serial.read()
        if file_serial == "" or int(file_serial) < current_serial:
            update = True
    else:
        f_serial = open(f"{db_folder}/{serial_filename}", "w")
        update = True

    if not update:
        print(f"{filename} is up to date at serial {file_serial.strip()}, skipping")
        irr_dbs.append(f"{db_folder}/{filename}")
        irr_serials.append(f"{filename}|{current_serial}")
        return

    print(f"{filename} is out of date at serial {file_serial.strip()} (current serial {current_serial}), downloading")

    try:
        CHUNK = 16 * 1024
        d = zlib.decompressobj(zlib.MAX_WBITS | 32)
        resp = request.urlopen(irr_source)
        with open(f"{db_folder}/{filename}", "wb") as f:
            while True:
                chungus = resp.read(CHUNK)
                if not chungus:
                    break
                f.write(d.decompress(chungus))

        irr_dbs.append(f"{db_folder}/{filename}")
        irr_serials.append(f"{filename}|{current_serial}")
        
        f_serial.seek(0)
        f_serial.write(str(current_serial))
        f_serial.truncate()
        f_serial.close()
        print(f"downloaded {filename}")
    except Exception as e:
        print(f"Error on writing {filename}, error:\n{str(e)}")
        if os.path.exists(f"{db_folder}/{serial_filename}"):
            os.remove(f"{db_folder}/{serial_filename}")
        if os.path.exists(f"{db_folder}/{filename}"):
            os.remove(f"{db_folder}/{filename}")


threads = []
for irr_source in irr_sources:
    thread = Thread(target=download, args=(irr_source[0], irr_source[1]))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

irr_serials.sort()
current_serial_hash = int(hashlib.md5(",".join(irr_serials).encode('utf-8')).hexdigest(), 16)
update = False
f_serial_hash = None
file_serial_hash = ""

if os.path.isfile(f"./{serial_hash_file}"):
    f_serial_hash = open(f"./{serial_hash_file}", "r+")
    file_serial_hash = f_serial_hash.read()
    if file_serial_hash == "" or int(file_serial_hash) != current_serial_hash:
        update = True
else:
    f_serial_hash = open(f"./{serial_hash_file}", "w")
    update = True

if not update:
    print(f"\n{serial_hash_file} is up to date with hash {file_serial_hash.strip()}, skipping")
    exit()

print(f"\n{export_file} is out of date, generating")

if os.path.exists(export_file):
    os.remove(export_file)

with open(export_file, "w") as f_out:
    for irr_db in irr_dbs:
        print(f"Processing {irr_db}")
        with open(irr_db, "rb") as f_in:
            line = f_in.readline()
            next_proc_item = ("route:", "route6:")
            cnt = 0
            while line:
                try:
                    line_text = line.decode().lower()
                except Exception:
                    pass

                if line_text.startswith(("route:", "route6:")) and line_text.startswith(next_proc_item):
                    f_out.write(f"{line_text}")
                    cnt += 1
                    next_proc_item = "origin:"
                elif line_text.startswith("origin:") and line_text.startswith(next_proc_item):
                    f_out.write(f"{line_text}")
                    cnt += 1
                    next_proc_item = ("source:")
                elif line_text.startswith("source:") and line_text.startswith(next_proc_item):
                    f_out.write(f"{line_text}")
                    cnt += 1
                    next_proc_item = ("route:", "route6:")

                line = f_in.readline()
            print(f"Processed {cnt} line(s)")

f_serial_hash.seek(0)
f_serial_hash.write(str(current_serial_hash))
f_serial_hash.truncate()
f_serial_hash.close()

print(f"Wrote everything to {export_file}")

os._exit(0)
