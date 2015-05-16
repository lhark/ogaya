#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import os

import ogayah as headless

OGAYA_PATHS = {
    "channels_list":"/home/{0}/.config/ogaya/channels.list".format(os.getlogin()),
    "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin()),
    "db":"/home/{0}/.config/ogaya/data.db".format(os.getlogin())
}

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
    print ("Channel already in the database")

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
