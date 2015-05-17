# Ogaya

Ogaya is an off-Google-account Youtube aggregator. It is designed as a backfire to Youtube's decision to "upgrade" [GDATA/RSS support](https://support.google.com/youtube/answer/6098135?hl=en).

It is essentially HTTP parsers, Python objects and a SQLite database to manipulate Youtube channels and videos.

Ogaya-CLI (ogayac) is a shell-like client for Ogaya.
Ogaya-Web (ogayaw) produce a grid of Youtube channels without any user-interactivity

## Requirements

### Python 3

### Docopt

On a Debian-like OS:

`sudo aptitude python3-docopt`

With PIP:

`sudo pip3 install docopt`

### Ogaya-CLI

Ogaya-CLi requires [youtube-dl](https://rg3.github.io/youtube-dl/).

