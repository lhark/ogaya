#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
OGAYA - Off-Google-Account Youtube Aggregator.

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
import ogayah as ogheadless

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

            self.channel.start_or_refresh(False)



class OgayaCLI(cmd.Cmd):
    """
    OgayaCLI shell.

    Availables commands:
        exit

        add

        down, downadd

        refresh

        cd, ls

        add_channel, rm_channel
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

    def cmdloop(self, *args, **kwargs):
        """
        Overwrite cmdloop just to redefine the input function in order
        to gracefully handle Ctrl-C
        """
        old_input_fn = cmd.__builtins__['input']
        cmd.__builtins__['input'] = input_swallowing_interrupt(old_input_fn)
        try:
            super().cmdloop(*args, **kwargs)
        finally:
            cmd.__builtins__['input'] = old_input_fn

    def preloop(self):
        db = self.paths["db"]

        if os.path.exists(db):
            conn = sqlite3.connect(db)
            c = conn.cursor()

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

            self._update_videos()

            self._motd(loaded)

        else:
            ogheadless.new_database(db)
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

    def _find_channel(self,channel_id):
        """
        Search a channel by its username/alias.

        Return it or None.
        """
        for channel in self.channels:
            if channel_id == channel.alias:
                return channel
            if channel_id == channel.username:
                return channel

        return None

    def _channel_selected(self):
        """Check if a channel is selected."""
        if self.cd_status == "@channels":
            return False
        else:
            return True

    def _clever_channels(self):
        """Produce a clever list of the channels username/alias."""
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
        """Load videos instances and their names"""
        videos = []
        videos_titles = []

        for channel in self.channels:
            for v in channel.videos:
                videos.append(v)
                videos_titles.append(v.name)

        self.videos = videos
        self.videos_titles = videos_titles

    def _download(self,args,url):
        """
        Download a video.

        args: youtube-dl args
        url:  URL of the video
        """
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

    def _add_channel(self,channel,alias=''):
        if channel:
            ok = False

            #--- Add the channel to the database -------------------------------

            if alias:
                try:
                    ogheadless.add_channel(
                        paths=self.paths,
                        channel=channel,
                        alias=alias
                    )

                    ok = True

                except ogheadless.ChannelAlreadyInDatabase:
                    print ("This channel is already in the database")

            else:
                try:
                    ogheadless.add_channel(
                        paths=self.paths,
                        channel=channel,
                    )

                    ok = True

                except ogheadless.ChannelAlreadyInDatabase:
                    print ("This channel is already in the database.")

            #--- Update the channel? -------------------------------------------

            if ok:
                try:
                    print ("Type ENTER to load immediatly the channel's videos")
                    print ("Or type CTRL-C.")

                    choice = input("\nENTER / CTRL-C")

                    try:
                        ogheadless.update_channel(
                            paths=self.paths,
                            channel=channel
                        )

                    except ogheadless.ChannelNotInDatabase:
                        print ("This channel is not in the database.")

                except KeyboardInterrupt:
                    pass

                #--- Adding the channel to OgayaCLI interface ----------------------

                if alias:
                    chan = ogobjects.YoutubeChannel(
                        username=channel,
                        alias=alias,
                        ogaya_paths=self.paths,
                        try_init=False
                    )
                else:
                    chan = ogobjects.YoutubeChannel(
                        username=channel,
                        ogaya_paths=self.paths,
                        try_init=False
                    )

                self._update_videos()


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

        for v in self.queue:
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



    def do_add_channel(self,line):
        """
        Add a new channel.

        add_channel channel_id
        add_channel channel_id|alias
        """

        if line:
            line = line.strip()

            if "|" in line:
                sline = line.split("|")

                channel_id, alias = sline[0].strip(), sline[1].strip()

                # A channel_id can't have space, so it is the
                # channel avatar. channel_id become alias and
                # alias become channel_id.

                if " " in sline[0]:
                    channel_id, alias = alias, channel_id

                self._add_channel(channel_id, alias)

            else:
                self._add_channel(line)

    def do_rm_channel(self,line):
        """
        Add a new channel.

        rm_channel channel_id
        rm_channel channel_alias
        """

        if line:
            channel = self._find_channel(line)

            if channel is None:
                print ("No channel/channel alias named '{0}'.".format(line))

            else:
                try:
                    # Remove the channel of the database

                    ogheadless.remove_channel(
                        paths=self.paths,
                        channel=channel.username
                    )

                    # Remove the channel's videos titles of the completions

                    videos_titles = [c.name for c in channel.videos]

                    for vt in videos_titles:
                        self.videos_titles.remove(vt)

                    # Remove the channel to the channels list

                    self.channels.remove(channel)

                    # Remove the channel to the channels' ID/alias list

                    self.channels_ids.remove(channel.username)

                    # Remove the videos belonging to the channel of the
                    # download queue.

                    for download in self.queue:
                        if download.channel == channel.username:
                            self.queue.remove(download)

                except ogheadless.ChannelNotInDatabase:
                    print ("This channel is not in the database.")




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
            if self.new_videos:
                for news in self.new_videos.items():
                    print ("Channel {0} {1}".format(news[0],30*"-"))

                    for count,video in enumerate(news[1]):
                        print ("\t{0}".format(video.name))
            else:
                print ("Nothing!")

    def do_ls(self,line):
        """List channels or known episodes of a channel."""

        if self._channel_selected():
            for count, video in enumerate(self.cd_status.videos):
                print ("{0} | {1}".format(count+1, video.name))

        else:
            print(
                    columnize(
                        self._clever_channels()
                    )
            )

    def _complete_channel(self, text, line, begidx, endidx):
        """Cmd completion function for commands requiring a channel"""

        arg = line.partition(' ')[2]
        off = len(arg) - len(text)
        if arg.endswith(' '):
            text = ' '
        elif arg.endswith('-'):
            text = '-'
        elif arg.endswith('#'):
            text = '#'
        if self._channel_selected():
            return []
        if not text:
            return self._clever_channels()
        else:
            return [c[off:] for c in self._clever_channels() if c.startswith(arg)]

    def _complete_video(self, text, line, begidx, endidx):
        """Cmd completion function for commands requiring a video"""

        arg = line.partition(' ')[2]
        off = len(arg) - len(text)
        if arg.endswith(' '):
            text = ' '
        elif arg.endswith('-'):
            text = '-'
        elif arg.endswith('#'):
            text = '#'
        if not text:
            if self._channel_selected():
                completions = [v.name for v in self.cd_status.videos]
            else:
                completions = self.videos_titles
        else:
            if self._channel_selected():
                completions = [v.name[off:] for v in self.cd_status.videos if v.name.startswith(arg)]
            else:
                completions = [v[off:] for v in self.videos_titles if v.startswith(arg)]

        return completions

    def complete_desc(self, text, line, begidx, endidx):
        """Cmd Completion function for desc"""
        return self._complete_channel(text, line, begidx, endidx)

    def complete_cd(self, text, line, begidx, endidx):
        """Cmd Completion function for cd"""
        return self._complete_channel(text, line, begidx, endidx)

    def complete_whatsnew(self, text, line, begidx, endidx):
        """Cmd Completion function for whatsnew"""
        return self._complete_channel(text, line, begidx, endidx)

    def complete_refresh(self, text, line, begidx, endidx):
        """Cmd Completion function for refresh"""
        return self._complete_channel(text, line, begidx, endidx)

    def complete_down(self, text, line, begidx, endidx):
        """Cmd Completion function for down"""
        return self._complete_video(text, line, begidx, endidx)

    def complete_add(self, text, line, begidx, endidx):
        """Cmd Completion function for add"""
        return self._complete_video(text, line, begidx, endidx)


# Fonctions =============================================================#

def input_swallowing_interrupt(_input):
    def _input_swallowing_interrupt(*args):
        try:
            return _input(*args)
        except KeyboardInterrupt:
            print('^C')
            return '\n'
    return _input_swallowing_interrupt


# Programme =============================================================#

if __name__ == "__main__":
    OGAYA_PATHS = ogutils.get_ogaya_paths()

    if not os.path.exists(OGAYA_PATHS["channels_dir"]):
        os.makedirs(OGAYA_PATHS["channels_dir"])

    #if not os.path.exists(OGAYA_PATHS["channels_list"]):
        #with open(OGAYA_PATHS["channels_list"],"w") as cl:
            #cl.write("ARTEplus7")

    ogaya = OgayaCLI(OGAYA_PATHS).cmdloop()

# vim:set shiftwidth=4 softtabstop=4:
