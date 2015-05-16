#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
OGAYA − Off-Google-Account Youtube Aggregator.

CLI client.

This is a backfire to the remove of  GDATA if you don't want to use a
Google account.
"""

# Imports ===============================================================#

import os
import sys
import cmd
import subprocess

import sqlite3

from threading import Thread, RLock

from columnize import *

import ogaya_parsers as ogparsers
import ogaya_objects as ogobjects
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class ChannelThread(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self)

        self.username = ''
        self.alias = ''
        self.description = ''

        self.paths = {}
        self.lock = None

        self.channel = None

        for key in kwargs:
            if key == "lock":
                self.lock = kwargs[key]

            if key == "username":
                self.username = kwargs[key]

            if key == "alias":
                self.alias = kwargs[key]

            if key == "description":
                self.description = kwargs[key]

            if key == "paths":
                self.paths = kwargs[key]

    def run(self):
        with self.lock:
            self.channel = ogobjects.YoutubeChannel(
                    username=self.username,
                    alias=self.alias,
                    description=self.description,
                    ogaya_paths=self.paths,
                    try_init=False
            )

            self.channel.start_or_refreshL(False)

class OgayaCLI(cmd.Cmd):
    """
    OgayaCLI shell.

    Availables commands:
        exit, add, down, downadd, refresh, cd, ls
    """

    def __init__(self,paths):
        cmd.Cmd.__init__(self)

        self.paths = paths

        self.prompt = "% / "

        self.channels = []
        self.channels_ids = []

        self.videos = []
        self.videos_titles = []
        self.queue = []

        self.ydl_args = [
                ["-f","43"],
                ["-f","18"]
        ]

        self.cd_status = "@channels"

    def preloop(self):

        db = self.paths["db"]

        conn = sqlite3.connect(db)
        c = conn.cursor()

        if os.path.exists(db):
            c.execute("SELECT * FROM Channel")
            cln = c.fetchall()

            channels = [
                {"username":cn[0],"alias":cn[1],"description":cn[2]} for cn in cln
            ]
            total = len(channels)

            load_lock = RLock()

            thrds = []


            for channel in channels:
                if not channel["username"] in self.channels_ids:
                    self.channels_ids.append(channel["username"])

                    thrds.append(
                            ChannelThread(
                                lock=load_lock,
                                username=channel["username"],
                                paths=self.paths,
                                alias=channel["alias"],
                                description=channel["description"]
                            )
                    )

                    thrds[-1].start()

            loaded = 0

            for t in thrds:
                t.join()

                loaded += 1

                align = int(len(str(total)) - len(str(loaded))) * "0"

                if t.alias:
                    print ("{0}{1} / {2} - {3}".format(align, loaded,total, t.alias))
                else:
                    print ("{0}{1} / {2} - {3}".format(align, loaded,total, t.username))

            for t in thrds:
                self.channels.append(t.channel)

            conn.close()
            self._motd(loaded)

        else:
            c.execute(
                '''CREATE TABLE Channel (Username text, Alias text, Description text);'''
            )
            conn.commit()

            c.execute(
                '''CREATE TABLE Channel (Url text, Name text, Description text, Channel text);'''
            )

            conn.commit()

            conn.close()
            self._motd()

    def postloop(self): pass

    def _motd(self,loaded=0):
        self._clear()

        print ("Ogaya\n")
        print ("OgayaCLI is under GNU GPL license.")
        print ("Use 'licence' for more information.\n")

        if loaded:
            print ("Loaded {0} channels".format(loaded))

    def _clear(self): os.system("clear")

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
            if channel.alias:
                channels.append(channel.alias)
            else:
                channels.append(channel.username)

        channels.sort()

        return channels

    def _refresh_new(self):
        self.new_videos = {}

        for channel in self.channels:
            if channel.new_videos:
                if channel.alias:
                    name = channel.alias
                else:
                    name = channel.username

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

    def _download(self,args,url):
        args = ["youtube-dl"] + args + [url]

        ret = subprocess.call(
                args,
                shell=False,
                stdout=open(os.devnull, 'wb')
        )

        if ret:
            return False
        else:
            return True

    def do_EOF(self, line):
        """Exit"""
        return True
    def do_licence(self): pass

    def do_exit(self,line):
        """Exit OgayaCLI"""
        sys.exit(0)

    def do_add(self,line):
        """Add a download in the queue."""
        video = None

        for vq in self.queue:
            if v.name == line:
                print ("This video is already in the queue.")
                break
            else:
                video = v
                break

        if video:
            self.queue.append(video)

    def do_down(self,line):
        """Download a video"""

        def _retry_download(url):
            try:
                print("New arguments for youtube-dl?")
                print("'Abort' or CTRL-C to abort.\n")
                nargs = input("Arguments % ")

                if nargs.lower() == "abort":
                    return False

                else:
                    success = self._download(nargs.split(),url)

                    if success:
                        print ("'{0}' downloaded.".format(line))
                    else:
                        _retry_download(url)

            except KeyboardInterrupt:
                return False
        def _try_args_variant(url):
            success = False

            for args_variant in self.ydl_args:
                success = self._download(args_variant,url)

                if success:
                    break

            if success:
                print ("'{0}' downloaded.".format(line))
                return True

            else:
                success = _retry_download(url)

                if not success:
                    print ("Aborted.")
                    return False

        if line:
            url = False

            if self._channel_selected():
                titles = [v.name for v in self.cd_status.videos]

                if line in titles:
                    for v in self.cd_status.videos:
                        if line == v.name:
                            url = v.url
                            break
            else:
                if line in self.videos_titles:
                    for v in self.videos_titles:
                        if line == v.name:
                            url = v.url
                            break

            if url:
                print ("Downloading '{0}'".format(line))
                _try_args_variant(url)

        else:
            if self.queue:
                results = []

                for video in self.queue:
                    print ("Downloading '{0}'".format(video.name))
                    success = _try_args_variant(video.url)

                    if success:
                        results.append(v.name)

                new_queue = []

                for video in self.queue:
                    if not video.name in results:
                        new_queue.append(video)

                self.queue = new_queue

            else:
                print ("No download scheduled.")

    def do_refresh(self,line):
        """Refresh a channel or all the channels"""

        if line:
            c = self._find_channel(line)

            if not c is None:
                c.start_or_refresh()
        else:
            for channel in self.channels:
                if channel.alias:
                    print ("Refresh",channel.alias)
                else:
                    print ("Refresh",channel.name)

                channel.start_or_refresh()

        self._update_videos()

    def do_desc(self,line):
        """Print the channel description"""

        if line:
            c = self._find_channel(line)

            if not c is None:
                if c.description:
                    print (
                        "\n{0}\n".format(
                            c.description
                        )
                    )
        else:
            if self._channel_selected():
                if self.cd_status.description:
                    print (
                        "\n{0}\n".format(
                            self.cd_status.description
                        )
                    )

    def do_cd(self,line):
        """CD around channels list & channel content"""

        if line:
            c = self._find_channel(line)

            if c is None:
                self.cd_status = "@channels"
                self.prompt = "% / "
            else:
                self.cd_status = c

                if c.alias:
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
            print(
                    columnize(
                        self._clever_channels()
                    )
            )

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
                completions = [v.name for v in self.cd_status.videos if v.name.startswith(text)]
            else:
                completions = [v for v in self.videos_titles if v.startswith(text)]

        return completions

    def complete_desc(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_cd(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_whatsnew(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_refresh(self, text, line, begidx, endidx):
        return self._complete_channel(text,line,begidx,endidx)
    def complete_down(self, text, line, begidx, endidx):
        return self._complete_video(text,line,begidx,endidx)
    def complete_add(self, text, line, begidx, endidx):
        return self._complete_video(text,line,begidx,endidx)


# Fonctions =============================================================#
# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = {
        "channels_list":"/home/{0}/.config/ogaya/channels.list".format(os.getlogin()),
        "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin()),
        "db":"/home/{0}/.config/ogaya/data.db".format(os.getlogin())
    }

    if not os.path.exists(OGAYA_PATHS["channels_dir"]):
        os.makedirs(OGAYA_PATHS["channels_dir"])

    if not os.path.exists(OGAYA_PATHS["channels_list"]):
        with open(OGAYA_PATHS["channels_list"],"w") as cl:
            cl.write("ARTEplus7")

    ogaya = OgayaCLI(OGAYA_PATHS).cmdloop()

# vim:set shiftwidth=4 softtabstop=4:
