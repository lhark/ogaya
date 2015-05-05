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
        self.channels = []
        self.channels_ids = []
        self.paths = paths

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

            return self.channels
        else:
            return False

# Fonctions =============================================================#


# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = {
        "channels_list":"/home/{0}/.config/ogaya/channels.list".format(os.getlogin()),
        "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin())
    }

    if not os.path.exists(OGAYA_PATHS["channels_dir"]):
        os.makedirs(OGAYA_PATHS["channels_dir"])

    if not os.path.exists(OGAYA_PATHS["channels_list"]):
        with open(OGAYA_PATHS["channels_list"],"w") as cl:
            cl.write("ARTEplus7")

    ogaya = HTMLRender(OGAYA_PATHS)
    s = ogaya.update_channels()

    for c in s:
        print (c.videos)

# vim:set shiftwidth=4 softtabstop=4:
