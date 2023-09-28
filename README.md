# slidcord

[Home](https://sr.ht/~nicoco/slidge) |
[Docs](https://slidge.im/slidcord) |
[Issues](https://todo.sr.ht/~nicoco/slidcord) |
[Patches](https://lists.sr.ht/~nicoco/public-inbox) |
[Chat](xmpp:slidge@conference.nicoco.fr?join)

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

# for the latest stable release (if any)
pipx install slidcord

# for the bleeding edge
pipx install slidcord \
    --pip-args='--extra-index-url https://slidge.im/repo'

slidcord --help
```

## Dev

```sh
git clone https://git.sr.ht/~nicoco/slidcord
cd slidcord
docker-compose up
```
