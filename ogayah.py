#!/usr/bin/python2
# -*- coding:Utf-8 -*-

"""
Ogaya headless interface

Communicate with Ogaya database.

Usage:
    ogayah add_channel [<channel_id>] [--alias=<channel_alias>]

Options:
  -h --help       Show this screen.
  --version       Show version.
"""

# Imports ===============================================================#

import os
import sys
#import subprocess

import sqlite3

from docopt import docopt

#import ogaya_parsers as ogparsers
import ogaya_objects as ogobjects
#import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class ChannelAlreadyInDatabase(Exception):
    """Exception if the channel is already in the Ogaya database"""
    pass

class ChannelNotInDatabase(Exception):
    """Exception if the channel is not in the Ogaya database"""
    pass

# Utility functions =====================================================#

def _db_has_channel(channel,db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(
            "SELECT * FROM Channel WHERE Username='{0}'".format(
                channel
            )
    )

    in_database = cursor.fetchall()

    conn.close()

    if in_database:
        return True
    else:
        return False

# Fonctions =============================================================#

def remove_channel(**kwargs):
    """
    Remove a channel.

    Arguments:
        cli (bool)       Fonction is used directly from ogayah(eadless).
                         False by default.

        paths (dict)     Ogaya paths. Or a dictionnary wich contains
                         the path of Ogaya database in "db" key.

        channel (string) Youtube ID of the channel, old or new style.

    Exceptions:

        ChannelNotInDatabase is raised... if the channel is not in the 
        database (thanks Captain Obvious).

    Examples:
        On a interface wich define OGAYA_PATHS as global:

            remove_channel(
                paths=OGAYA_PATHS,
                channel="UCsqvprYnU8J8K449VAQZhsQ",
            )

        With a dummy paths dictionnary:

            remove_channel(
                paths={"db":"/home/foobar/.config/ogaya/data.db"},
                channel="UCsqvprYnU8J8K449VAQZhsQ",
            )
    """
    is_cli = False
    paths = {}

    channel = ''

    for key in kwargs:
        if key == "cli":
            is_cli = kwargs[key]
        if key == "paths":
            paths = kwargs[key]
        if key == "channel":
            channel = kwargs[key]

    if is_cli:
        if not paths:
            paths = OGAYA_PATHS

    if channel:
        if _db_has_channel(channel,paths["db"]):
            conn = sqlite3.connect(paths["db"])
            cursor = conn.cursor()

            # Delete all the videos of the channel
            cursor.execute(
                    'DELETE FROM Video WHERE Channel="{0}";'.format(
                            channel
                        )
            )
            conn.commit()

            # Delete the channel
            cursor.execute(
                    'DELETE FROM Channel WHERE Username="{0}";'.format(
                            channel
                        )
            )
            conn.commit()

            conn.close()

            return True

        else:
            raise ChannelNotInDatabase()

    else:
        return False

def update_channel(**kwargs):
    """
    Update a channel.

    Arguments:
        cli (bool)       Fonction is used directly from ogayah(eadless).
                         False by default.

        paths (dict)     Ogaya paths. Or a dictionnary wich contains
                         the path of Ogaya database in "db" key.

        channel (string) Youtube ID of the channel, old or new style.

    Exceptions:

        ChannelNotInDatabase is raised... if the channel is not in the 
        database (thanks Captain Obvious).

    Examples:
        On a interface wich define OGAYA_PATHS as global:

            update_channel(
                paths=OGAYA_PATHS,
                channel="UCsqvprYnU8J8K449VAQZhsQ",
            )

        With a dummy paths dictionnary:

            update_channel(
                paths={"db":"/home/foobar/.config/ogaya/data.db"},
                channel="UCsqvprYnU8J8K449VAQZhsQ",
            )
    """
    is_cli = False
    paths = {}

    channel = ''

    for key in kwargs:
        if key == "cli":
            is_cli = kwargs[key]
        if key == "paths":
            paths = kwargs[key]
        if key == "channel":
            channel = kwargs[key]

    if is_cli:
        if not paths:
            paths = OGAYA_PATHS

    if channel:
        if _db_has_channel(channel,paths["db"]):
            channel_object = ogobjects.YoutubeChannel(
                    username=username,
                    alias=alias,
                    description=description,
                    ogaya_paths=paths
            )

            return True

        else:
            raise ChannelNotInDatabase()

    else:
        return False


def add_channel(**kwargs):
    """
    Add a new channel to the Ogaya database.

    DOES NOT update it's content! -> ogayah.update_channel

    Arguments:
        cli (bool)       Fonction is used directly from ogayah(eadless).
                         False by default.

        paths (dict)     Ogaya paths. Or a dictionnary wich contains
                         the path of Ogaya database in "db" key.

        channel (string) Youtube ID of the channel, old or new style.

        alias (string)   Alias for the channel. Particularly usefull
                         if channel use the new style, unreadable by
                         humans...

    Exceptions:

        ChannelAlreadyInDatabase is raised... if the channel is already
        in the database (thanks Captain Obvious).

    Examples:
        On a interface wich define OGAYA_PATHS as global:

            add_new_channel(
                paths=OGAYA_PATHS,
                channel="UCsqvprYnU8J8K449VAQZhsQ",
                alias="Videotheque d'Alexandrie"
            )

        With a dummy paths dictionnary:

            add_new_channel(
                paths={"db":"/home/foobar/.config/ogaya/data.db"},
                channel="UCsqvprYnU8J8K449VAQZhsQ",
                alias="Videotheque d'Alexandrie"
            )
    """

    is_cli = False
    paths = {}

    channel, alias = '', ''

    for key in kwargs:
        if key == "cli":
            is_cli = kwargs[key]
        if key == "paths":
            paths = kwargs[key]
        if key == "channel":
            channel = kwargs[key]
        if key == "alias":
            alias = kwargs[key]

    if is_cli:
        if not paths:
            paths = OGAYA_PATHS

    if channel:
        if _db_has_channel(channel,paths["db"]):
            raise ChannelAlreadyInDatabase()

        else:
            conn = sqlite3.connect(paths["db"])
            cursor = conn.cursor()

            if alias:
                cursor.execute(
                        "INSERT INTO Channel VALUES ('{0}','{1}','')".format(
                            channel, alias
                        )
                )
            else:
                cursor.execute(
                        "INSERT INTO Channel VALUES ('{0}','','')".format(
                            channel
                        )
                )

            conn.commit()
            conn.close()

            return True

    else:
        return False

# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = {
        "channels_list":"/home/{0}/.config/ogaya/channels.list".format(os.getlogin()),
        "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin()),
        "db":"/home/{0}/.config/ogaya/data.db".format(os.getlogin())
    }

    arguments = docopt(__doc__, version='0.1')

    CURDIR = "{0}{1}".format(os.path.realpath(os.curdir),os.sep)

    for arg in ["add_channel"]:
        if arguments[arg]:
            operation,valid = arg,True

    if valid:
        retcode = 0

        if operation == "add_channel":

            if arguments["<channel_id>"]:
                if arguments["--alias"] is None:
                    alias = False
                else:
                    alias = arguments["--alias"]

                try:
                    add_new_channel(
                        cli=True,
                        channel=arguments["<channel_id>"],
                        alias=alias
                    )
                except ChannelAlreadyInDatabase:
                    print ("Channel was already in the database")

            else:
                print ("No channel ID given!")
                retcode = 1

    else:
        retcode = 1

    sys.exit(retcode)

# vim:set shiftwidth=4 softtabstop=4:
