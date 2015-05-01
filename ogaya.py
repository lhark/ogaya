#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
OGAYA − Off-Google-Account Youtube Aggregator.

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

class OgayaCLI(cmd.Cmd):
    """
    OgayaCLI shell.

    Availables commands:
        exit, add, down, downadd, refresh, cd, ls
    """

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "% / "

        self.channels = []
        self.channels_ids = []

        self.videos = []
        self.videos_titles = []

        self.ydl_args = ["-f","43"]

        self.cd_status = "@channels"

    def motd(self,loaded=0):
        self._clear()

        print ("Ogaya\n")
        print ("OgayaCLI is under GNU GPL license.")
        print ("Use 'licence' for more information.\n")

        if loaded:
            print ("Loaded {0} channels".format(loaded))

    def _clear(self): os.system("clear")

    def preloop(self):
        if os.path.exists(os.path.realpath("channels.list")):
            print ("Loading Youtube Channels videos")

            with open(os.path.realpath("channels.list"),"r") as cl:
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
                                        alias=alias
                                    )
                            )
                        else:
                            self.channels.append(ogobjects.YoutubeChannel(username=line))

                        loaded += 1
                        print ("Loaded: {0}".format(loaded))

            self._update_videos()

            self.motd(loaded)
        else:
            self.motd()

    def postloop(self): pass

    def _find_channel(self,s):
        for channel in self.channels:
            if s == channel.alias:
                return channel
            if s == channel.username:
                return channel

        return None

    def _channel_selected(self):
        if self.cd_status == "@channels":
            return False
        else:
            return True

    def _clever_channels(self):
        channels = []

        for channel in self.channels:
            if channel.alias is None:
                channels.append(channel.username)
            else:
                channels.append(channel.alias)

        channels.sort()

        return channels

    def _refresh_new(self):
        self.new_videos = {}

        for channel in self.channels:
            if channel.new_videos:
                if channel.alias is None:
                    name = channel.username
                else:
                    name = channel.alias

                self.new_videos[name] = []

                for video in channel.new_videos:
                    self.new_videos[name].append(video)

    def _update_videos(self):
        videos = []
        videos_titles = []

        for channel in self.channels:
            for v in channel.videos:
                videos.append(v)
                videos_titles.append(v.name)

        self.videos = videos
        self.videos_titles = videos_titles

    def do_EOF(self, line):
        """Exit"""
        return True

    def do_licence(self): pass

    def do_exit(self,line):
        """Exit OgayaCLI"""
        sys.exit(0)

    def do_add(self,line):
        """Documentation for add"""
        pass

    def do_down(self,line):
        """Documentation for down"""
        pass

        #args = ["youtube-dl"] + self.ydl_args + [video_url]
        #ret = subprocess.Popen(args,stdout=subprocess.DEVNULL)
        #print (ret)

    def do_downview(self,line):
        """Documentation for downview"""
        pass

    def do_downadd(self,line):
        """Documentation for downadd"""
        pass

    def do_refresh(self,line):
        """Refresh a channel or all the channels"""

        if line:
            c = self._find_channel(line)

            if not c is None:
                c.start_or_refresh()
        else:
            for channel in self.channels:
                channel.start_or_refresh()

        self._update_videos()

    def do_cd(self,line):
        """CD around channels list & channel content"""

        if line:
            c = self._find_channel(line)

            if c is None:
                self.cd_status = "@channels"
                self.prompt = "% / "
            else:
                self.cd_status = c

                if c.alias is None:
                    self.prompt = "% /{0}/ ".format(c.username)
                else:
                    self.prompt = "% /{0}/ ".format(c.alias)

        else:
            self.cd_status = "@channels"
            self.prompt = "% / "

    def do_whatsnew(self,line):
        if line:
            if line in self._clever_channels():
                self._refresh_new()

                if line in self.new_videos.keys():
                    for count,video in enumerate(self.new_videos[line]):
                        print (count+1,"|",video.name)
        else:
            for news in self.new_videos.items():
                print ("Channel {0} {1}".format(news[0],30*"-"))

                for count,video in enumerate(news[1]):
                    print ("\t{0}".format(video.name))

    def do_ls(self,line):
        """List channels or known episodes of a channel."""

        if self._channel_selected():
            for count,video in enumerate(self.cd_status.videos):
                print (count+1,"|",video.name)

        else:
            for channel in self._clever_channels():
                print (channel)

    def _complete_channel(self, text, line, begidx, endidx):
        if self._channel_selected():
            return []
        else:
            if not text:
                completions = self._clever_channels()
            else:
                completions = [c for c in self._clever_channels() if c.startswith(text)]

            return completions

    def _complete_video(self, text, line, begidx, endidx):
        if not text:
            if self._channel_selected():
                completions = [v.name for v in self.cd_status.videos]
            else:
                completions = self.videos_titles
        else:
            if self._channel_selected():
                completions = [v.name for v in self.cd_status.videos if v.startswith(text)]
            else:
                completions = [v for v in self.videos_titles if v.startswith(text)]

        return completions

    def complete_cd(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_whatsnew(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_refresh(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_down(self, text, line, begidx, endidx):
        return self._complete_video(text,line,begidx,endidx)


# Fonctions =============================================================#
# Programme =============================================================#

if __name__ == "__main__":
    ogaya = OgayaCLI().cmdloop()

# vim:set shiftwidth=4 softtabstop=4:
