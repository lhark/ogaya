#!/usr/bin/python2
# -*- coding:Utf-8 -*-

"""
Ogaya headless interface

Communicate with Ogaya database.

Usage:
    ogayah add_channel <channel_id> [--alias=<channel_alias>]
    ogayah update_channel <channel_id>
    ogayah remove_channel <channel_id>
    ogayah new_database [--path=<arbitrary_path>] [--force]

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
import ogaya_utils as ogutils

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
    """Check if the channel channel is in the Ogaya database db"""

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Channel WHERE Username=(?)", (channel,))

    in_database = cursor.fetchall()

    conn.close()

    return bool(in_database)

# Fonctions =============================================================#

def new_database(path):
    """
    Make a empty Ogaya Database.

    Arguments:
        path (string) Path of the new database.

       If  you are  not testing  things,  it is  a  good idea  to get
       Ogaya standard paths with

            paths_dict = ogaya_utils.get_ogaya_paths()

       and use paths_dict["db"] as path argument.

    Exceptions:

        (OSError.)FileExistsError (python builtin) if the database path
        match an existing file.

    Examples:
        new_database("/home/foobar/test.db")
    """

    path = os.path.realpath(path)

    if os.path.exists(path):
        raise FileExistsError()

    else:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        cursor.execute(
            '''CREATE TABLE Channel (Username text, Alias text, Description text);'''
        )
        conn.commit()

        cursor.execute(
            '''CREATE TABLE Video (Url text, Name text, Description text, Channel text);'''
        )

        conn.commit()

        conn.close()

        return True


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

    if not channel:
        return False

    if _db_has_channel(channel, paths["db"]):
        conn = sqlite3.connect(paths["db"])
        cursor = conn.cursor()

        # Delete all the videos of the channel
        cursor.execute('DELETE FROM Video WHERE Channel=(?)', (channel,))
        conn.commit()

        # Delete the channel
        cursor.execute('DELETE FROM Channel WHERE Username=(?)', (channel,))
        conn.commit()

        conn.close()

        return True

    else:
        raise ChannelNotInDatabase()


def update_channel(**kwargs):
    """
    Update a channel.

    Arguments:
        cli (bool)       Fonction is used directly from ogayah(eadless).
                         False by default.

        paths (dict)     Ogaya paths. Or a dictionnary wich contains
                         the path of Ogaya database in "db" key.

        channel (string) Youtube ID of the channel, old or new style.

        gui (bool)       If True, updating the channel will download
                         GUI interfaces intersting files (like avatar
                         picture of the channel).

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

    gui=True

    for key in kwargs:
        if key == "cli":
            is_cli = kwargs[key]
        if key == "paths":
            paths = kwargs[key]
        if key == "channel":
            channel = kwargs[key]
        if key == "gui":
            gui = kwargs[key]

    if is_cli:
        if not paths:
            paths = OGAYA_PATHS

    if not channel:
        return False

    if _db_has_channel(channel, paths["db"]):
        channel_object = ogobjects.YoutubeChannel(
            username=channel,
            ogaya_paths=paths,
            try_init=False
        )
        channel_object.start_or_refresh(refresh=True, gui=gui)

        return True

    else:
        raise ChannelNotInDatabase()


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

            add_channel(
                paths=OGAYA_PATHS,
                channel="UCsqvprYnU8J8K449VAQZhsQ",
                alias="Videotheque d'Alexandrie"
            )

        With a dummy paths dictionnary:

            add_channel(
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

    if not channel:
        return False

    if _db_has_channel(channel, paths["db"]):
        raise ChannelAlreadyInDatabase()

    else:
        conn = sqlite3.connect(paths["db"])
        cursor = conn.cursor()

        if alias:
            cursor.execute(
                    "INSERT INTO Channel VALUES (?,?,?)",
                    (channel, alias, "")
            )
        else:
            cursor.execute(
                    "INSERT INTO Channel VALUES (?,?,?)",
                    (channel, "", "")
            )

        conn.commit()
        conn.close()

        return True

# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = ogutils.get_ogaya_paths()

    arguments = docopt(__doc__, version='0.1')

    CURDIR = "{0}{1}".format(os.path.realpath(os.curdir),os.sep)

    for arg in ["add_channel","remove_channel","update_channel","new_database"]:
        if arguments[arg]:
            operation,valid = arg,True

    if valid:
        retcode = 0

        #--- Remove a channel --------------------------------------------------

        if operation == "remove_channel":
            if arguments["<channel_id>"]:
                try:
                    remove_channel(
                        cli=True,
                        channel=arguments["<channel_id>"]
                    )
                except ChannelNotInDatabase:
                    print ("Channel was not in the database")
            else:
                print ("No channel ID given!")
                retcode = 1

        #--- Update a channel --------------------------------------------------

        elif operation == "update_channel":
            if arguments["<channel_id>"]:
                try:
                    update_channel(
                        cli=True,
                        channel=arguments["<channel_id>"]
                    )
                except ChannelNotInDatabase:
                    print ("Channel was not in the database")
            else:
                print ("No channel ID given!")
                retcode = 1

        #--- Add a channel -----------------------------------------------------

        elif operation == "add_channel":

            if arguments["<channel_id>"]:
                if arguments["--alias"] is None:
                    alias = False
                else:
                    alias = arguments["--alias"]

                try:
                    add_channel(
                        cli=True,
                        channel=arguments["<channel_id>"],
                        alias=alias
                    )
                except ChannelAlreadyInDatabase:
                    print ("Channel was already in the database")

            else:
                print ("No channel ID given!")
                retcode = 1

        #--- Make a new database -----------------------------------------------

        elif operation == "new_database":

            if arguments["--path"] is None:
                path = OGAYA_PATHS["db"]
            else:
                path = arguments["--path"]

            path = os.path.realpath(path)

            if arguments["--force"]:
                force = True
            else:
                force = False

            if os.path.exists(path):
                if force:
                    os.remove(path)
                    new_database(path)

                else:
                    print ("File {0} already exists. Erase it and make new database?")

                    try:
                        done = False
                        while not done:
                            choice = input("yes/no ? ")

                            if choice:
                                choice = choice.lower()

                                if choice[0] in ["y","n"]:
                                    if choice.startswith("y"):
                                        os.remove(path)
                                        new_database(path)

                                    done = True

                    except KeyboardInterrupt:
                        pass

            else:
                new_database(path)

        #-----------------------------------------------------------------------

    else:
        retcode = 1

    sys.exit(retcode)

# vim:set shiftwidth=4 softtabstop=4:
