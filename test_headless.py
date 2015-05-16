#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Test file for Ogaya Headless.

Replace TEST_DIR with your own test folder.
"""

import os
import sys

import ogayah as headless

#--- Configuration -------------------------------------------------------------

TEST_DIR = "/home/etienne/GIT/Mes dépôts/ogaya/tests"

OGAYA_PATHS = {
    "channels_dir":"{0}/channels/".format(TEST_DIR),
    "db":"{0}/data.db".format(TEST_DIR)
}

#--- Cleaning things before testing and setting up -----------------------------

os.remove(OGAYA_PATHS["db"])

if not os.path.exists(OGAYA_PATHS["channels_dir"]):
    os.makedirs(OGAYA_PATHS["channels_dir"])

#--- Make a new database -------------------------------------------------------

headless.new_database(OGAYA_PATHS["db"])

try:
    headless.new_database(OGAYA_PATHS["db"])
except FileExistsError:
    print ("OK - Database already exists")

#--- Adding channel ------------------------------------------------------------

headless.add_channel(
    channel='ARTEplus7',
    alias='Arte +7',
    paths=OGAYA_PATHS
)

try:
    headless.add_channel(
        channel='ARTEplus7',
        alias='Arte +7',
        paths=OGAYA_PATHS
    )
except headless.ChannelAlreadyInDatabase:
    print ("OK - Channel already in the database")

#--- Updating channel ----------------------------------------------------------

headless.update_channel(
    channel='ARTEplus7',
    paths=OGAYA_PATHS
)

#--- Removing channel ----------------------------------------------------------

headless.remove_channel(
    channel='ARTEplus7',
    paths=OGAYA_PATHS
)

try:
    headless.remove_channel(
        channel='ARTEplus7',
        paths=OGAYA_PATHS
    )
except headless.ChannelNotInDatabase:
    print ("Channel is not in the database")

# vim:set shiftwidth=4 softtabstop=4:
