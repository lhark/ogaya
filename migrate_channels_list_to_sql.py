#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import sqlite3

if __name__ == "__main__":

    channels = "/home/etienne/.config/ogaya/channels.list"
    db = "/home/etienne/GIT/Mes dépôts/ogaya/data.db"

    conn = sqlite3.connect(db)
    c = conn.cursor()

    with open(channels,"r") as cf:
        for line in cf:
            line = line.rstrip()

            if "|" in line:
                sline = line.split("|")
                sline = [s.strip() for s in sline]

                username, alias = sline[0], sline[1]

                c.execute(
                        "SELECT * FROM Channel WHERE Username='{0}'".format(
                            username
                        )
                )
                users = c.fetchall()

                if not users:
                    c.execute(
                            "INSERT INTO Channel VALUES ('{0}','{1}','')".format(
                                username,
                                alias
                            )
                    )
                    conn.commit()

                users = False

            else:
                c.execute(
                        "SELECT * FROM Channel WHERE Username='{0}'".format(
                            line
                        )
                )
                users = c.fetchall()

                if not users:
                    c.execute(
                            "INSERT INTO Channel VALUES ('{0}','','')".format(
                                line
                            )
                    )
                    conn.commit()

                users = False

    conn.close()

# vim:set shiftwidth=4 softtabstop=4:
