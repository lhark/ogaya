#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Ogaya utilitary functions
"""

# Imports ===============================================================#

import os
import urllib.request

import ogaya_parsers as ogparsers

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Fonctions =============================================================#

def get_base_ogaya_path():
    return "/home/{0}/.config/ogaya/".format(os.getlogin())

def get_ogaya_paths():
    return {
        "channels_list":"/home/{0}/.config/ogaya/channels.list".format(os.getlogin()),
        "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin()),
        "db":"/home/{0}/.config/ogaya/data.db".format(os.getlogin())
    }

def download(url,target):
    try:
        urllib.request.urlretrieve(url,target)
    except ValueError:
        pass

def get_urls(user,action):

    if action == "description":
        styles = {
                "old":'https://www.youtube.com/user/{0}/about',
                "new":'https://www.youtube.com/channel/{0}/about',
        }

        local_filename = False

        for style in styles:
            try:
                page = styles[style].format(user)
                local_filename,headers = urllib.request.urlretrieve(page)

                if local_filename:
                    return {
                            "content":open(local_filename,"r").read(),
                            "tempfile":local_filename,
                            "page":page
                           }

            except urllib.request.HTTPError:
                pass

        return {}

    if action == "videos":
        styles = {
                "old":'https://www.youtube.com/user/{0}/videos',
                "new":'https://www.youtube.com/channel/{0}/videos',
        }

        local_filename = False

        for style in styles:
            try:
                page = styles[style].format(user)
                local_filename,headers = urllib.request.urlretrieve(page)

                if local_filename:
                    return {
                            "content":open(local_filename,"r").read(),
                            "tempfile":local_filename,
                            "page":page
                           }

            except urllib.request.HTTPError:
                pass

        return {}

    if action == "avatar":
        styles = {
                "old":'https://www.youtube.com/user/{0}/',
                "new":'https://www.youtube.com/channel/{0}/',
        }

        for style in styles:
            try:
                page = styles[style].format(user)
                local_filename,headers = urllib.request.urlretrieve(page)

                if local_filename:
                    html = open(local_filename,"r").read()

                    avatar = ogparsers.AvatarParser().get_avatar(html)

                    if avatar:
                        os.remove(local_filename)

                    return avatar

            except urllib.request.HTTPError:
                pass

        return False

# vim:set shiftwidth=4 softtabstop=4:
