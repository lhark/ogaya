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

from threading import Thread, RLock

import ogaya_parsers as ogparsers
import ogaya_objects as ogobjects
import ogaya_utils as ogutils

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Columnize package =====================================================#
# Copyright (C) 2008-2010, 2013 Rocky Bernstein <rocky@gnu.org>.'''
# License : Python Software Foundation License',

def computed_displaywidth():
    '''Figure out a reasonable default with. Use os.environ['COLUMNS'] if possible,
    and failing that use 80.
    '''
    width=80
    if 'COLUMNS' in os.environ:
        try: 
            width = int(os.environ['COLUMNS'])
        except:
            pass
        pass
    return width

default_opts = {
    'arrange_array'    : False,  # Check if file has changed since last time
    'arrange_vertical' : True,  
    'array_prefix'     : '',
    'array_suffix'     : '',
    'colfmt'           : None,
    'colsep'           : '  ',
    'displaywidth'     : computed_displaywidth,
    'lineprefix'       : '',
    'linesuffix'       : "\n",
    'ljust'            : None,
    'term_adjust'      : False
    }

def get_option(key, options):
    global default_opts
    if key not in options:
        return default_opts.get(key)
    else:
        return options[key]
    return None # Not reached

def columnize(array, displaywidth=80, colsep = '  ', 
              arrange_vertical=True, ljust=True, lineprefix='',
              opts={}):
    """Return a list of strings as a compact set of columns arranged 
    horizontally or vertically.

    For example, for a line width of 4 characters (arranged vertically):
        ['1', '2,', '3', '4'] => '1  3\n2  4\n'

    or arranged horizontally:
        ['1', '2,', '3', '4'] => '1  2\n3  4\n'

    Each column is only as wide as necessary.  By default, columns are
    separated by two spaces - one was not legible enough. Set "colsep"
    to adjust the string separate columns. Set `displaywidth' to set
    the line width. 

    Normally, consecutive items go down from the top to bottom from
    the left-most column to the right-most. If "arrange_vertical" is
    set false, consecutive items will go across, left to right, top to
    bottom."""
    if not isinstance(array, list) and not isinstance(array, tuple): 
        raise TypeError((
            'array needs to be an instance of a list or a tuple'))

    o = {}
    if len(opts.keys()) > 0:
        for key in default_opts.keys():
            o[key] = get_option(key, opts)
            pass
        if o['arrange_array']:
            o['array_prefix'] = '['
            o['lineprefix']   = ' '
            o['linesuffix']   = ",\n"
            o['array_suffix'] = "]\n"
            o['colsep']       = ', '
            o['arrange_vertical'] = False
            pass

    else:
        o = default_opts.copy()
        o['displaywidth']     = displaywidth
        o['colsep']           = colsep
        o['arrange_vertical'] = arrange_vertical
        o['ljust']            = ljust
        o['lineprefix']       = lineprefix
        pass

    # if o['ljust'] is None:
    #     o['ljust'] = !(list.all?{|datum| datum.kind_of?(Numeric)})
    #     pass

    if o['colfmt']:
        array = [(o['colfmt'] % i) for i in array]
    else:
        array = [str(i) for i in array]
        pass

    # Some degenerate cases
    size = len(array)
    if 0 == size: 
        return "<empty>\n"
    elif size == 1:
        return '%s%s%s\n' % (o['array_prefix'], str(array[0]),
                             o['array_suffix'])

    if o['displaywidth'] - len(o['lineprefix']) < 4:
        o['displaywidth'] = len(o['lineprefix']) + 4
    else:
        o['displaywidth'] -= len(o['lineprefix'])
        pass

    o['displaywidth'] = max(4, o['displaywidth'] - len(o['lineprefix']))
    if o['arrange_vertical']:
        array_index = lambda nrows, row, col: nrows*col + row
        # Try every row count from 1 upwards
        for nrows in range(1, size):
            ncols = (size+nrows-1) // nrows
            colwidths = []
            totwidth = -len(o['colsep'])
            for col in range(ncols):
                # get max column width for this column
                colwidth = 0
                for row in range(nrows):
                    i = array_index(nrows, row, col)
                    if i >= size: break
                    x = array[i]
                    colwidth = max(colwidth, len(x))
                    pass
                colwidths.append(colwidth)
                totwidth += colwidth + len(o['colsep'])
                if totwidth > o['displaywidth']: 
                    break
                pass
            if totwidth <= o['displaywidth']: 
                break
            pass
        # The smallest number of rows computed and the
        # max widths for each column has been obtained.
        # Now we just have to format each of the
        # rows.
        s = ''
        for row in range(nrows):
            texts = []
            for col in range(ncols):
                i = row + nrows*col
                if i >= size:
                    x = ""
                else:
                    x = array[i]
                texts.append(x)
            while texts and not texts[-1]:
                del texts[-1]
            for col in range(len(texts)):
                if o['ljust']:
                    texts[col] = texts[col].ljust(colwidths[col])
                else:
                    texts[col] = texts[col].rjust(colwidths[col])
                    pass
                pass
            s += "%s%s%s" % (o['lineprefix'], str(o['colsep'].join(texts)),
                             o['linesuffix'])
            pass
        return s
    else:
        array_index = lambda ncols, row, col: ncols*(row-1) + col
        # Try every column count from size downwards
        colwidths = []
        for ncols in range(size, 0, -1):
            # Try every row count from 1 upwards
            min_rows = (size+ncols-1) // ncols
            for nrows in range(min_rows, size):
                rounded_size = nrows * ncols
                colwidths = []
                totwidth  = -len(o['colsep'])
                for col in range(ncols):
                    # get max column width for this column
                    colwidth  = 0
                    for row in range(1, nrows+1):
                        i = array_index(ncols, row, col)
                        if i >= rounded_size: break
                        elif i < size:
                            x = array[i]
                            colwidth = max(colwidth, len(x))
                            pass
                        pass
                    colwidths.append(colwidth)
                    totwidth += colwidth + len(o['colsep'])
                    if totwidth >= o['displaywidth']: 
                        break
                    pass
                if totwidth <= o['displaywidth'] and i >= rounded_size-1:
                    # Found the right nrows and ncols
                    nrows  = row
                    break
                elif totwidth >= o['displaywidth']:
                    # Need to reduce ncols
                    break
                pass
            if totwidth <= o['displaywidth'] and i >= rounded_size-1:
                break
            pass
        # The smallest number of rows computed and the
        # max widths for each column has been obtained.
        # Now we just have to format each of the
        # rows.
        s = ''
        if len(o['array_prefix']) != 0:
            prefix = o['array_prefix']
        else:
            prefix = o['lineprefix'] 
            pass
        for row in range(1, nrows+1):
            texts = []
            for col in range(ncols):
                i = array_index(ncols, row, col)
                if i >= size:
                    break
                else: x = array[i]
                texts.append(x)
                pass
            for col in range(len(texts)):
                if o['ljust']:
                    texts[col] = texts[col].ljust(colwidths[col])
                else:
                    texts[col] = texts[col].rjust(colwidths[col])
                    pass
                pass
            s += "%s%s%s" % (prefix, str(o['colsep'].join(texts)),
                             o['linesuffix'])
            prefix = o['lineprefix']
            pass
        s += o['array_suffix']
        return s
    pass
#========================================================================#

# Classes ===============================================================#

class ChannelThread(Thread):
    def __init__(self, lock, username, paths, alias=False):
        Thread.__init__(self)

        self.lock = lock

        self.username = username
        self.paths = paths
        self.alias = alias

        self.channel = None

    def run(self):
        with self.lock:
            if self.alias:
                self.channel = ogobjects.YoutubeChannel(
                        username=self.username,
                        alias=self.alias,
                        ogaya_paths=self.paths
                )
            else:
                self.channel = ogobjects.YoutubeChannel(
                        username=self.username,
                        ogaya_paths=self.paths
                )

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
        if os.path.exists(self.paths["channels_list"]):
            print ("Loading Youtube Channels videos")

            load_lock = RLock()

            thrds = []

            with open(self.paths["channels_list"],"r") as cl:

                total = 0

                for line in cl:
                    if not line.startswith("#"):
                        total += 1
                        line = line.rstrip()

                        if "|" in line:
                            sline = line.split("|")

                            user, alias = sline[0], sline[1]

                            if not user in self.channels_ids:
                                self.channels_ids.append(user)

                                thrds.append(
                                        ChannelThread(
                                            load_lock,
                                            user,
                                            self.paths,
                                            alias
                                        )
                                )

                                thrds[-1].start()

                        else:
                            if not line in self.channels_ids:
                                self.channels_ids.append(line)

                                thrds.append(
                                        ChannelThread(
                                            load_lock,
                                            line,
                                            self.paths
                                        )
                                )

                                thrds[-1].start()

            #for t in thrds:
                #t.start()

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

            self._update_videos()

            self._motd(loaded)
        else:
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
        "channels_dir":"/home/{0}/.config/ogaya/channels/".format(os.getlogin())
    }

    if not os.path.exists(OGAYA_PATHS["channels_dir"]):
        os.makedirs(OGAYA_PATHS["channels_dir"])

    if not os.path.exists(OGAYA_PATHS["channels_list"]):
        with open(OGAYA_PATHS["channels_list"],"w") as cl:
            cl.write("ARTEplus7")

    ogaya = OgayaCLI(OGAYA_PATHS).cmdloop()

# vim:set shiftwidth=4 softtabstop=4:
