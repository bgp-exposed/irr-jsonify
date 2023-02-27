#!/usr/bin/env python3

import_file = "./irr.db"
export_file = "./irrdb.json"


import os
import time

tm = int(time.time())

def asdot_to_asplain(str):
    split = str.split(".")
    if len(split) == 2:
        dot = int(split[0] or "0")
        add = int(split[1] or "0")
        return (dot * 65536) + add
    else:
        return None


with open(export_file, "w") as f_out:
    f_out.writelines([
        "{\n",
        "    \"roas\": ["
    ])

    with open(import_file, "r") as f_in:
        print(f"{import_file} is properly opened, processing")
        proc_cnt = 0
        line = f_in.readline()
        prefix = None
        asn = None
        source = None
        next_proc_item = "route"
        cnt = 0
        while line:
            variables = line.split(":")

            attrib = variables[0].strip().lower() or ""
            val = (":".join(variables[1:])).strip().split()[0].upper() or ""

            if attrib.startswith(next_proc_item) and len(val) > 0:
                if attrib.startswith("route"):
                    prefix = val.lower()
                    next_proc_item = "origin"

                if attrib.startswith("origin"):
                    val = val.replace("AS", "")
                    if "." not in val:
                        asn = f"AS{val}"
                    else:
                        asn = f"AS{asdot_to_asplain(val)}"
                    next_proc_item = "source"

                if attrib.startswith("source"):
                    source = val.upper()

            if prefix and asn and source:
                if "." in prefix:
                    maxlen = 24
                    prefixlen = 32
                elif ":" in prefix:
                    maxlen = 48
                    prefixlen = 128
                else:
                    maxlen = 1
                    prefixlen = 32

                if "/" in prefix:
                    prefixlen = int(prefix.split("/")[1])

                if prefixlen <= maxlen:
                    f_out.write(f"\n        {{\"asn\": \"{asn}\", \"prefix\": \"{prefix}\", \"maxLength\": {maxlen}, \"ta\": \"{source}\"}},")
                    proc_cnt += 1
                prefix = None
                asn = None
                next_proc_item = "route"

            line = f_in.readline()
        if proc_cnt > 0:
            # remove last comma
            f_out.seek(0, os.SEEK_END)
            pos = f_out.tell() - 1
            f_out.seek(pos, os.SEEK_SET)
            f_out.truncate()

    f_out.writelines([
        "\n    ],\n",
        "    \"metadata\": {\n",
        "        \"builder\": \"irr2json\",\n",
        f"        \"generated\": {tm},\n",
        f"        \"valid\": {tm + 86400},\n",
        f"        \"counts\": {proc_cnt}\n",
        "    }\n",
        "}"
    ])


print(f"{export_file} written")
