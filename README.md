# slidcord

A
[feature-rich](https://slidge.im/slidcord/features.html)
[Discord](https://discord.com) to
[XMPP](https://xmpp.org/) puppeteering
[gateway](https://xmpp.org/extensions/xep-0100.html), based on
[slidge](https://slidge.im) and
[discord.py-self](https://discordpy-self.readthedocs.io).

[![builds.sr.ht status](https://builds.sr.ht/~nicoco/slidcord/commits/master/ci.yml.svg)](https://builds.sr.ht/~nicoco/slidcord/commits/master/ci.yml)
[![containers status](https://builds.sr.ht/~nicoco/slidcord/commits/master/container.yml.svg)](https://builds.sr.ht/~nicoco/slidcord/commits/master/container.yml)
[![pypi status](https://badge.fury.io/py/slidcord.svg)](https://pypi.org/project/slidcord/)

## Installation

Refer to the [slidge admin documentation](https://slidge.im/core/admin/)
for general info on how to set up an XMPP server component.

### Containers

From [dockerhub](https://hub.docker.com/r/nicocool84/slidcord)

```sh
docker run docker.io/nicocool84/slidcord
```

### Python package

With [pipx](https://pypa.github.io/pipx/):

```sh
pipx install slidcord  # for the latest tagged release
slidcord --help
```

For the bleeding edge, download artifacts of
[this build job](https://builds.sr.ht/~nicoco/slidcord/commits/master/ci.yml).

## Dev

```sh
git clone https://git.sr.ht/~nicoco/slidcord
cd slidcord
docker-compose up
```
