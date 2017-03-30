#!/usr/bin/python3
# -*- coding:Utf-8 -*-

# Migration script for those who still use channels.list
# Will be removed soon

import os
from os.path import expanduser
import sqlite3

if __name__ == "__main__":

    channels = "{0}/.config/ogaya/channels.list".format(expanduser("~"))
    channels_dir = "{0}/.config/ogaya/channels/".format(expanduser("~"))
    db = "{0}/.config/ogaya/data.db".format(expanduser("~"))

    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Populate Channel table
    with open(channels,"r") as cf:
        for line in cf:
            line = line.rstrip()

            if "|" in line:
                sline = line.split("|")
                sline = [s.strip() for s in sline]

                username, alias = sline[0], sline[1]

                c.execute(
                        "SELECT * FROM Channel WHERE Username=(?)", (username,)
                )
                users = c.fetchall()

                if not users:
                    c.execute(
                            "INSERT INTO Channel VALUES (?,?,?)",
                            (username, alias, "")
                    )
                    conn.commit()

                users = False

            else:
                c.execute(
                        "SELECT * FROM Channel WHERE Username=(?)", (line,)
                )
                users = c.fetchall()

                if not users:
                    c.execute(
                            "INSERT INTO Channel VALUES (?,?,?)", (line, "", "")
                    )
                    conn.commit()

                users = False

    # Populate Video table
    for f in os.listdir(channels_dir):
        fp = os.path.realpath("{0}{1}".format(channels_dir,f))

        if os.path.isfile(fp):
            if f.endswith(".videos"):
                username = f.split(".videos")[0]

                c.execute(
                        "SELECT * FROM Video WHERE Channel=(?)", (username,)
                )
                videos = c.fetchall()

                if not videos:

                    with open(fp,"r") as cvf:
                        for line in cvf:
                            line = line.rstrip()

                            sline = line.split("|")

                            url, name = sline[0], sline[1]
                            print (url,name)

                            c.execute(
                                    'INSERT INTO Video VALUES (?,?,?,?)',
                                    (url, name, "", username)
                            )
                            conn.commit()

    conn.close()

# vim:set shiftwidth=4 softtabstop=4:
