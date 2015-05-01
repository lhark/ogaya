#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
OGAYA − Off-Google-Account Youtube Aggregator.

Tests file.

This is a backfire to the remove of  GDATA if you don't want to use a
Google account.
"""

# Imports ===============================================================#

import os

import ogaya_parsers as ogparsers
import ogaya_objects as ogobjects
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#
# Fonctions =============================================================#
# Programme =============================================================#

if __name__ == "__main__":
    # Youtube channel with the traditionnal naming system

    old = ogobjects.YoutubeChannel(
            username="ArtePlus7",
            alias="Arte +7"
            )

    old.update("start")

    for v in old.videos:
        print (v.name,v.url)

    input("Press ENTER to continue")

    # Youtube channel with the new naming system

    new = ogobjects.YoutubeChannel(
            username="UCCMxHHciWRBBouzk-PGzmtQ",
            alias="Bazar du grenier"
            )
    new.update("start")

    for v in new.videos:
        print (v.name,v.url)

    input("Press ENTER to continue")

    # Download an channel avatar

    avatar = ogutils.get_urls("ArtePlus7","avatar")
    ogutils.download(avatar,"arteplus7.{0}".format(avatar.split(".")[-1]))

    input("Press ENTER to continue")

    # Get latest videos of a channel avoiding YoutubeChannel
    # object, but not YoutubeVideo object

    feed = ogutils.get_urls("ArtePlus7","videos")
    print ("Webpage",feed["page"])
    print ("Webpage tempfile",feed["tempfile"])

    input("Press ENTER to continue")

    print ("Webpage content",feed["content"])

    input("Press ENTER to continue")

    os.remove(feed["tempfile"])

    parser = ogparsers.YTParser()
    videos = parser.get_videos(feed["content"])

    for v in videos:
        print (v.name,v.url)

    input("Press ENTER to continue")

# vim:set shiftwidth=4 softtabstop=4:
