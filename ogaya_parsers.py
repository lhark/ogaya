#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
HTML Parsers used by Ogaya to get datas.
"""

# Imports ===============================================================#

import urllib.request

from html.parser import HTMLParser

import ogaya_objects as ogobjects

# Classes ===============================================================#

class AvatarParser(HTMLParser):
    """Get channel/user avatar by parsing channel/user main page."""

    def __init__(self):
        HTMLParser.__init__(self)

        self.is_avatar = False
        self.avatar_link = False

    def get_avatar(self,html):
        self.feed(html)

        return self.avatar_link

    def handle_starttag(self, tag, attrs):
        img_classes = ["channel-header-profile-image","appbar-nav-avatar"]

        if not self.avatar_link:
            if tag == "img":
                if attrs:
                    for attr in attrs:
                        if attr[0] == "class":
                            for ic in img_classes:
                                if ic in attr[1]:
                                    self.is_avatar = True
                                    break

                    if self.is_avatar:
                        for attr in attrs:
                            if attr[0] == "src":
                                self.avatar_link = attr[1]
                                self.is_avatar = False

class YTParser(HTMLParser):
    """Parse Youtube /user/videos page"""

    def __init__(self):
        HTMLParser.__init__(self)

        self.videos = []
        self.current_video = ogobjects.YoutubeVideo()

        self.wait_video = False
        self.wait_link = False

    def get_videos(self,html):
        self.feed(html)

        return self.videos

    def handle_starttag(self, tag, attrs):
        if tag in ["div","h3","a"]:

            if tag == "div":
                if attrs:
                    for attr in attrs:
                        if attr[0] == "class" and "yt-lockup-content" in attr[1]:
                            self.wait_video = True

            if self.wait_video:
                if tag == "h3":
                    if attrs:
                        for attr in attrs:
                            if attr[0] == "class" and "yt-lockup-title" in attr[1]:
                                self.wait_link = True
                                self.wait_video = False

            if self.wait_link:
                if tag == "a":
                    if attrs:
                        for attr in attrs:
                            self.current_video = ogobjects.YoutubeVideo()

                            if attr[0] == "href":
                                if attr[1].startswith("/watch"):
                                    self.current_video.url = "https://www.youtube.com/watch?v={0}".format(attr[1].split('?v=')[-1])
                                else:
                                    self.wait_link = False

    def handle_endtag(self, tag):
        if tag in ["div","h3","a"]:
            if tag == "a" and self.wait_link:
                self.wait_link = False
                self.videos.append(self.current_video)
                self.current_video = ogobjects.YoutubeVideo()

    def handle_data(self, data):
        if self.wait_link:
            self.current_video.name = data

# Fonctions =============================================================#
# Programme =============================================================#

#if __name__ == "__main__": pass

# vim:set shiftwidth=4 softtabstop=4:
