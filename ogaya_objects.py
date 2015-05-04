#!/usr/bin/python3
# -*- coding:Utf-8 -*-

""" Docstring! """

# Imports ===============================================================#

import os

import ogaya_parsers as ogparsers
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class YoutubeChannel:
    def __init__(self,**kwargs):
        self.videos = []

        self.new_videos = []

        self.username = None
        self.alias = None

        self.description = ""

        self.try_init = True
        self.valid = False

        for key in kwargs:
            if key == "username" or key == "channel":
                self.username = kwargs[key]
            if key == "alias":
                self.alias = kwargs[key]
            if key == "try_init":
                self.try_init = kwargs[key]

        if self.try_init:
            if self.username is None:
                print ("No username!")
            else:
                self.start_or_refresh()

    def save_channel_file(self):
        channel_file = "channels/{0}.videos".format(self.username)

        if os.path.exists(os.path.realpath(channel_file)):
            os.remove(os.path.realpath(channel_file))

        with open(channel_file,"w") as cf:
            for video in self.videos:
                cf.write("{0}|{1}\n".format(video.url,video.name))

    def set_videos_urls(self):
        self.videos_urls = []

        for video in self.videos:
            if not video.url is None:
                self.videos_urls.append(video.url)

    def start_or_refresh(self):
        channel_file = "channels/{0}.videos".format(self.username)

        if os.path.exists(channel_file):
            with open(channel_file,"r") as cf:
                for line in cf:
                    line = line.rstrip()

                    if not line.startswith("#"):
                        sline = line.split("|")

                        self.videos.append(
                                YoutubeVideo(
                                    url=sline[0],
                                    name=sline[1]
                                )
                        )

            self.set_videos_urls()

            self.update("refresh")
        else:
            self.update("start")

    def update(self,mode="start",gui=True):
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

                        target = "channels/{0}.{1}".format(self.username,pic.split(".")[-1])

                        ogutils.download(pic,target)
                    else:
                        self.have_avatar = False

                else:
                    self.have_avatar = False

                self.valid = True

            else:
                self.valid = False

                print ("This channel/user doesn't exist.")

class YoutubeVideo:
    def __init__(self,**kwargs):
        self.url = None
        self.name = None

        for key in kwargs:
            if key == "url":self.url = kwargs[key]
            if key == "name":self.name = kwargs[key]

    def __str__(self):
        return "{0} − {1}".format(self.name,self.url)

# Fonctions =============================================================#
# Programme =============================================================#

#if __name__ == "__main__": pass

# vim:set shiftwidth=4 softtabstop=4:
