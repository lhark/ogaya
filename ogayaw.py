#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
OGAYA − Off-Google-Account Youtube Aggregator.

HTML output.

This is a backfire to the remove of  GDATA if you don't want to use a
Google account.
"""

# Imports ===============================================================#

import os
import sys
import webbrowser

import sqlite3

from threading import Thread, RLock

import ogaya_parsers as ogparsers
import ogaya_objects as ogobjects
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class ChannelThread(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self)

        self.username = ''
        self.alias = ''
        self.description = ''

        self.paths = {}
        self.lock = None

        self.channel = None

        for key in kwargs:
            if key == "lock":
                self.lock = kwargs[key]

            if key == "username":
                self.username = kwargs[key]

            if key == "alias":
                self.alias = kwargs[key]

            if key == "description":
                self.description = kwargs[key]

            if key == "paths":
                self.paths = kwargs[key]

    def run(self):
        with self.lock:
            self.channel = ogobjects.YoutubeChannel(
                    username=self.username,
                    alias=self.alias,
                    description=self.description,
                    ogaya_paths=self.paths,
                    try_init=False
            )

            self.channel.start_or_refresh(False)

class HTMLRender:
    def __init__(self,paths):
        self.paths = paths

        self.channels = []
        self.channels_ids = []

        self.updated = False

    def _clean_up(self):
        for channel in self.channels:
            os.remove(
                "{0}{1}.html".format(
                    self.paths["web_dir"],
                    channel.username
                )
            )

    def _render_index(self):
        def _render_case(channel,paths):
            if channel.alias is None:
                name = channel.username
            else:
                name = channel.alias

            avatar_path = "{0}{1}.jpg".format(
                        paths["channels_dir"],
                        channel.username
                    )

            channel_file = "{0}{1}.html".format(
                    paths["web_dir"],
                    channel.username
            )

            if os.path.exists(avatar_path):
                avatar = True
            else:
                avatar = False

            if name:
                if avatar:
                    case = '\t\t\t<section><h3>{0}</h3><div class="avatar"><a href="{1}"><img src="{2}" /></a></div></section>\n'.format(
                                name,
                                channel_file,
                                avatar_path
                            )
                else:
                    case = '\t\t\t<section><h3><a href="{1}">{0}</a></h3></section>\n'.format(
                                name,
                                channel_file
                            )

                return case
            else:
                return ''

        head = ''
        for l in [
                '<!DOCTYPE html>\n',
                '<html>\n',
                '\t<head>',
                '\t\t<meta charset=utf-8 />',
                '\t\t<title>Ogaya</title>',
                '\t\t<link rel="stylesheet" type="text/css" media="screen" href="grid.css" />',
                '\t</head>',
                '\t<body>',
                '\t\t<header><h1>Ogaya</h1></header>',
                '\t\t<article>']:
            head += "{0}\n".format(l)

        tail = '\t\t</article>\n\t</body>\n</html>'

        index_file = "{0}index.html".format(self.paths["web_dir"])

        if os.path.exists(index_file):
            os.remove(index_file)

        with open(index_file,"w") as index:
            index.write(head)

            for channel in self.successful:
                index.write(_render_case(channel,self.paths))

            index.write(tail)

    def _render_channel(self,channel):
        head = """<!DOCTYPE html>
<html>
    <head>
	<meta charset=utf-8 />
	<title>Ogaya</title>
	<link rel="stylesheet" type="text/css" media="screen" href="grid.css" />
    </head>

    <body>
        <header><a href="index.html"><h1>Ogaya</h1></a></header>
        """

        tail = '\n    </body>\n</html>'

        channel_file = "{0}{1}.html".format(
                self.paths["web_dir"],
                channel.username
        )

        with open(channel_file,"w") as cf:
            cf.write(head)

            cf.write("<article>\n")
            cf.write("<ol>\n")

            for video in channel.videos:
                cf.write(
                    '<li><a href="{0}">{1}</a></li>\n'.format(
                        video.url,
                        video.name
                    )
                )

            cf.write("</ol>\n")
            cf.write("</article>\n")

            cf.write(tail)

            return True

        return False

    def render(self):
        if self.updated:
            self.successful = []

            for channel in self.channels:
                rc = self._render_channel(channel)

                if rc:
                    self.successful.append(channel)

            if self.successful:
                self._render_index()

                return True

            else:
                self._clean_up()

                return False

        else:
            self.update_channels()
            self.render()

    def update_channels(self):
        db = self.paths["db"]

        if os.path.exists(db):
            conn = sqlite3.connect(db)
            c = conn.cursor()

            c.execute("SELECT * FROM Channel")
            cln = c.fetchall()

            channels = [
                {"username":cn[0],"alias":cn[1],"description":cn[2]} for cn in cln
            ]
            total = len(channels)

            load_lock = RLock()
            thrds = []

            for channel in channels:
                if not channel["username"] in self.channels_ids:
                    self.channels_ids.append(channel["username"])

                    thrds.append(
                            ChannelThread(
                                lock=load_lock,
                                username=channel["username"],
                                paths=self.paths,
                                alias=channel["alias"],
                                description=channel["description"]
                            )
                    )

                    thrds[-1].start()

            loaded = 0

            for t in thrds:
                t.join()

                loaded += 1

                align = int(len(str(total)) - len(str(loaded))) * "0"

                if t.alias:
                    print ("{0}{1} / {2} - {3}".format(align, loaded,total, t.alias))
                else:
                    print ("{0}{1} / {2} - {3}".format(align, loaded,total, t.username))

            for t in thrds:
                self.channels.append(t.channel)

            conn.close()

            self.updated = True
            return self.channels

        else:
            return False

# Fonctions =============================================================#


# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = ogutils.get_ogaya_paths()
    OGAYA_PATHS["web_dir"] = "{0}ogaweb/".format(ogutils.get_base_ogaya_path())

    if not os.path.exists(OGAYA_PATHS["web_dir"]):
        os.makedirs(OGAYA_PATHS["web_dir"])

    # Clean the web_dir
    for f in os.listdir(OGAYA_PATHS["web_dir"]):
        if os.path.isfile(f):
            if f.endswith(".html"):
                os.remove("{0}{1}".format(OGAYA_PATHS["web_dir"],f))

    ogaya = HTMLRender(OGAYA_PATHS)
    s = ogaya.update_channels()

    success = ogaya.render()

    if success:
        try:
            view = input("Press ENTER to open ogaweb page or CTRL-C to cancel")
            webbrowser.open("{0}index.html".format(OGAYA_PATHS["web_dir"]))
        except KeyboardInterrupt:
            sys.exit(0)

# vim:set shiftwidth=4 softtabstop=4:
