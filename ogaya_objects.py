#!/usr/bin/python3
# -*- coding:Utf-8 -*-

""" Docstring! """

# Imports ===============================================================#

import os

import sqlite3

import ogaya_parsers as ogparsers
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class YoutubeChannel:
    def __init__(self, **kwargs):
        """
        Youtube Channel object.
        """

        self.videos = []

        self.new_videos = []

        self.username = None
        self.alias = None

        self.description = ""

        self.try_init = True
        self.valid = False

        self.ogaya_paths = {}

        for key in kwargs:
            if key == "username" or key == "channel":
                self.username = kwargs[key]

            if key == "alias":
                self.alias = kwargs[key]

            if key == "try_init":
                self.try_init = kwargs[key]

            if key == "ogaya_paths":
                self.ogaya_paths = kwargs[key]

            if key == "description":
                self.description = kwargs[key]

        if self.try_init:
            if self.username is None:
                print ("No username!")
            else:
                self.start_or_refresh()

    def __str__(self):
        return "{0} channel".format(self.username)

    def save_channel_file(self):
        if self.ogaya_paths:
            db = self.ogaya_paths["db"]
        else:
            channel_file = "data.db"

        conn = sqlite3.connect(db)
        c = conn.cursor()


        c.execute(
                "SELECT * FROM Channel WHERE Username='{0}'".format(
                    self.username
                )
        )
        users = c.fetchall()

        if not users:
            c.execute(
                    "INSERT INTO Channel VALUES ('{0}','{1}','')".format(
                        self.username,
                        self.alias
                    )
            )
            conn.commit()

        for video in self.videos:
            c.execute("SELECT * FROM Video WHERE Url='{0}'".format(video.url))
            in_db = c.fetchall()

            if not in_db:
                c.execute(
                    'INSERT INTO Video VALUES ("{0}","{1}","","{2}")'.format(
                        video.url,
                        video.name,
                        self.username)
                )

                conn.commit()

        conn.close()

    def set_videos_urls(self):
        self.videos_urls = []

        for video in self.videos:
            if not video.url is None:
                self.videos_urls.append(video.url)

    def retrieve_videos(self):
        if self.ogaya_paths:
            db = self.ogaya_paths["db"]
        else:
            channel_file = "data.db"

        conn = sqlite3.connect(db)
        c = conn.cursor()

        c.execute(
                "SELECT * FROM Video WHERE Channel='{0}'".format(
                    self.username
                )
        )
        videos = c.fetchall()

        conn.close()

        return videos

    def start_or_refresh(self,refresh=True):
        videos = self.retrieve_videos()

        if videos:
            if not self.videos:
                for v in videos:
                    vo = YoutubeVideo(
                        url=v[0],
                        name=v[1],
                        description=v[2],
                        channel=self
                    )
                    self.videos.append(vo)

            if refresh:
                self.update("refresh")
        else:
            self.update("start")

    def update(self,mode="start", gui=True):
        def _add_videos(obj,mode):
            feed = ogutils.get_urls(obj.username,"videos")

            if feed:
                html = feed["content"]
                page = feed["page"]
                tempfile = feed["tempfile"]

                parser = ogparsers.YTParser()

                for v in parser.get_videos(html):
                    if mode == "start":
                        obj.videos.append(v)
                    elif mode == "refresh":
                        if not v.url in obj.videos_urls:
                            obj.videos.append(v)
                            obj.new_videos.append(v)
                    else:
                        raise ValueError(
                            "Invalid YoutubeChannel.update() mode:{0}".format(mode)
                        )

                del(parser)
                os.remove(tempfile)

                success = True
            else:
                success = False

            return success,obj

        def _set_description(obj):
            feed = ogutils.get_urls(obj.username,"description")
            html = feed["content"]

            aboutparser = ogparsers.AboutParser()
            description = aboutparser.get_description(html)

            obj.description = description

            return obj

        if not self.username is None:
            feed,self = _add_videos(self,mode)

            if feed:
                self.set_videos_urls()
                self = _set_description(self)

                if mode == "start":
                    self.save_channel_file()

                if gui:
                    pic = ogutils.get_urls(self.username,"avatar")

                    if pic:
                        self.have_avatar = True

                        if self.ogaya_paths:
                            target = "{0}{1}.{2}".format(
                                    self.ogaya_paths["channels_dir"],
                                    self.username,
                                    pic.split(".")[-1]
                            )
                        else:
                            target = "channels/{0}.{1}".format(
                                    self.username,
                                    pic.split(".")[-1]
                            )

                        ogutils.download(pic,target)
                    else:
                        self.have_avatar = False

                else:
                    self.have_avatar = False

                self.valid = True

            else:
                self.valid = False

                print (
                        "This channel/user '{0}' doesn't exist.".format(
                            self.username
                        )
                )

    def to_SQL(self,db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute(
                "INSERT INTO Channel VALUES ('{0}','{1}','{2}')".format(
                    self.username,
                    self.alias,
                    self.description
                )
        )
        conn.commit()
        conn.close()

class YoutubeVideo:
    def __init__(self, **kwargs):
        self.url = None
        self.name = None
        self.description = None

        self.channel = None

        for key in kwargs:
            if key == "url":
                self.url = kwargs[key]
            if key == "name":
                self.name = kwargs[key]
            if key == "description":
                self.description = kwargs[key]
            if key == "channel":
                self.channel = kwargs[key].username

    def to_SQL(self, db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute(
                "INSERT INTO Videos VALUES ('{0}','{1}','{2}','{3}')".format(
                    self.url,
                    self.name,
                    self.description,
                    self.channel
                )
        )
        conn.commit()
        conn.close()

    def __str__(self):
        return "{0} − {1}".format(self.name,self.url)

# Fonctions =============================================================#
# Programme =============================================================#

#if __name__ == "__main__": pass

# vim:set shiftwidth=4 softtabstop=4:
