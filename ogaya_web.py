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
import cmd
import subprocess

import ogaya_parsers as ogparsers
import ogaya_objects as ogobjects
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

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
                    case = '<section><h3>{0}</h3><div class="avatar"><a href="{1}"><img src="{2}" /></a></div></section>'.format(
                                name,
                                channel_file,
                                avatar_path
                            )
                else:
                    case = '<section><h3><a href="{1}">{0}</a></h3></section>'.format(
                                name,
                                channel_file
                            )
            else:
                return ''

        head = """<!DOCTYPE html>
<html>
    <head>
	<meta charset=utf-8 />
	<title>Ogaya</title>
	<link rel="stylesheet" type="text/css" media="screen" href="grid.css" />
    </head>

    <body>
        <header><h1>Ogaya</h1></header>
        <article>"""

        tail = '        </article>\n    </body>\n</html>'

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
        <header><h1><a href="index.html">Ogaya</a></h1></header>
        <article>"""

        tail = '        </article>\n    </body>\n</html>'

        channel_file = "{0}{1}.html".format(
                paths["web_dir"],
                channel.username
        )

        with open(channel_file,"w") as cf:
            cf.write(head)

            cf.write("<section>")
            cf.write("<ol>")

            for video in channel.videos:
                cf.write(
                    '<li><a href="{0}">{1}</a></li>'.format(
                        video.url,
                        video.name
                    )
                )

            cf.write("</ol>")
            cf.write("</section>")

            cf.write(tail)

            return True

        return False

    def render(self):
        if self.updated:
            self.successful = []

            for channel in self.channels:
                rc = self._render_channel(self,channel)

                if rc:
                    self.successful.append(channel)

            if self.successful:
                self._render_index()
            else:
                self._clean_up()

        else:
            self.update_channels()
            self.render()

    def update_channels(self):
        if os.path.exists(self.paths["channels_list"]):
            print ("Loading Youtube Channels videos")

            with open(self.paths["channels_list"],"r") as cl:
                loaded = 0

                for line in cl:
                    line = line.rstrip()

                    if not line in self.channels_ids:
                        if "|" in line:
                            sline = line.split("|")

                            user,alias = sline[0],sline[1]

                            self.channels.append(
                                    ogobjects.YoutubeChannel(
                                        username=user,
                                        alias=alias,
                                        ogaya_paths=self.paths
                                    )
                            )

                        else:
                            self.channels.append(
                                    ogobjects.YoutubeChannel(
                                        username=line,
                                        ogaya_paths=self.paths
                                    )
                            )

                        self.channels[-1].start_or_refresh()

                        loaded += 1
                        print ("Loaded: {0}".format(loaded))

            self.updated = True

            return self.channels
        else:
            return False

# Fonctions =============================================================#


# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = {
        "channels_list":"/home/{0}/.config/ogaya/channels.list".format(os.getlogin()),
        "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin()),
        "web_dir":"/home/{0}/.config/ogaya/web/".format(os.getlogin())
    }

    if not os.path.exists(OGAYA_PATHS["channels_dir"]):
        os.makedirs(OGAYA_PATHS["channels_dir"])

    if not os.path.exists(OGAYA_PATHS["web_dir"]):
        os.makedirs(OGAYA_PATHS["web_dir"])

    if not os.path.exists(OGAYA_PATHS["channels_list"]):
        with open(OGAYA_PATHS["channels_list"],"w") as cl:
            cl.write("ARTEplus7")

    ogaya = HTMLRender(OGAYA_PATHS)
    s = ogaya.update_channels()

    for c in s:
        print (c.videos)

# vim:set shiftwidth=4 softtabstop=4:
