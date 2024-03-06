import logging
from typing import Optional

import discord as di
import discord.utils
from slidge import BaseGateway, FormField
from slidge.util.util import get_version  # noqa: F401
from slixmpp import JID

from . import commands, config, contact, group, session  # noqa: F401


async def _get_build_number(sess) -> int:
    """Fetches client build number"""
    default_build_number = 9999
    try:
        login_page_request = await sess.get("https://discord.com/login", timeout=7)
        login_page = await login_page_request.text()
        build_url = (
            "https://discord.com/assets/"
            + discord.utils.re.compile(r"assets/+([a-z0-9.]+)\.js").findall(login_page)[
                -2
            ]
            + ".js"
        )
        build_request = await sess.get(build_url, timeout=7)
        build_file = await build_request.text()
        build_find = discord.utils.re.findall(r'Build Number:\D+"(\d+)"', build_file)
        return int(build_find[0]) if build_find else default_build_number
    except Exception:
        discord.utils._log.critical(
            "Could not fetch client build number. Falling back to hardcoded value..."
        )
        return default_build_number


discord.utils._get_build_number = _get_build_number  # type: ignore


class Gateway(BaseGateway):
    COMPONENT_NAME = "Discord (slidge)"
    COMPONENT_TYPE = "discord"
    COMPONENT_AVATAR = "https://www.usff.fr/wp-content/uploads/2018/05/Discord_logo.png"

    REGISTRATION_INSTRUCTIONS = "Have a look at https://discordpy-self.readthedocs.io/en/latest/authenticating.html"
    REGISTRATION_FIELDS = [FormField("token", label="Discord token", required=True)]

    ROSTER_GROUP = "Discord"

    GROUPS = True

    def __init__(self):
        super().__init__()
        if not config.DISCORD_VERBOSE:
            log.debug("Disabling discord info logs")
            logging.getLogger("discord.gateway").setLevel(logging.WARNING)
            logging.getLogger("discord.client").setLevel(logging.WARNING)

    async def validate(
        self, user_jid: JID, registration_form: dict[str, Optional[str]]
    ):
        token = registration_form.get("token")
        assert isinstance(token, str)
        try:
            await di.Client().login(token)
        except di.LoginFailure as e:
            raise ValueError(str(e))


__version__ = get_version()

log = logging.getLogger(__name__)
