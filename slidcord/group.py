from datetime import datetime
from typing import Optional, Union

import discord as di
import discord.errors
from slidge import LegacyBookmarks, LegacyMUC, LegacyParticipant, MucType
from slixmpp.exceptions import XMPPError

from . import config
from .contact import Contact
from .session import Session
from .util import MessageMixin, StatusMixin


class Bookmarks(LegacyBookmarks[int, "MUC"]):
    session: Session

    async def fill(self):
        for channel in self.session.discord.get_all_channels():
            if isinstance(channel, di.TextChannel):
                try:
                    await self.by_legacy_id(channel.id)
                except XMPPError as e:
                    self.log.debug("Skipping %s because of %s", channel, e)

        for private_channel in self.session.discord.private_channels:
            self.log.debug("Private channel: %s", private_channel)
            if isinstance(private_channel, di.DMChannel):
                continue
            try:
                muc = await self.by_legacy_id(private_channel.id)
            except XMPPError as e:
                self.log.debug("Skipping %s because of %s", private_channel, e)
                continue

            await muc.add_to_bookmarks()


class Participant(StatusMixin, MessageMixin, LegacyParticipant):
    session: Session
    contact: Contact

    @property
    def discord_user(self) -> Union[di.User, di.ClientUser]:  # type:ignore
        if self.contact is None:
            return self.session.discord.user  # type:ignore

        return self.contact.discord_user


class MUC(LegacyMUC[int, int, Participant, int]):
    session: Session

    async def get_discord_channel(self) -> Union[di.TextChannel, di.GroupChannel]:
        await self.session.discord.wait_until_ready()
        channel = self.session.discord.get_channel(self.legacy_id)  # type: ignore
        if not isinstance(channel, (di.GroupChannel, di.TextChannel)):
            raise XMPPError(
                "bad-request", f"This is not a valid textual discord channel: {channel}"
            )
        return channel

    async def get_user_participant(self):
        p = await super().get_user_participant()
        p.discord_id = self.session.discord.user.id  # type:ignore
        return p

    async def fill_participants(self):
        chan = await self.get_discord_channel()
        for m in await self.members():
            if m.id == self.session.discord.user.id:  # type:ignore
                await self.get_user_participant()
                continue
            co = await self.session.contacts.by_discord_user(m)
            p = await self.get_participant_by_contact(co)
            if isinstance(chan, di.TextChannel):
                if chan.guild.owner == m:
                    p.role = "moderator"
                    p.affiliation = "owner"
            if isinstance(m, di.Member):
                p.update_status(m.status, m.activity)

    async def members(self):
        chan = await self.get_discord_channel()
        if isinstance(chan, di.GroupChannel):
            return chan.nicks  # type: ignore
        else:
            return chan.members  # type: ignore

    async def user_member(self):
        try:
            me = next(
                m
                for m in await self.members()
                if m.id == self.session.discord.user.id  # type:ignore
            )
        except StopIteration:
            return None
        return me

    async def update_info(self):
        chan = await self.get_discord_channel()
        if not chan:
            raise XMPPError(
                "item-not-found", f"Can't retrieve info discord on {self.legacy_id}"
            )
        if isinstance(chan, di.GroupChannel):
            self.type = MucType.GROUP
            await self._update_group(chan)
        else:
            self.type = MucType.CHANNEL_NON_ANONYMOUS
            await self._update_guild_channel(chan)

    async def _update_guild_channel(self, chan: di.TextChannel):
        me = await self.user_member()
        if not me:
            raise XMPPError(
                "registration-required", f"You are not a member of {self.name}"
            )

        if not chan.permissions_for(me).read_messages:
            raise XMPPError(
                "forbidden", f"You are not allowed to read messages in {self.name}"
            )

        if chan.category:
            self.name = (
                f"{chan.guild.name}/{chan.position:02d}/{chan.category}/{chan.name}"
            )
        else:
            self.name = f"{chan.guild.name}/{chan.position:02d}/{chan.name}"
        self.subject = chan.topic
        self.n_participants = chan.guild.approximate_member_count
        if icon := chan.guild.icon:
            self.avatar = str(icon)

    async def _update_group(self, chan: di.GroupChannel):
        if chan.name:
            self.name = chan.name
        else:
            recipients = [
                x
                for x in chan.recipients
                if x.id != self.session.discord.user.id  # type:ignore
            ]

            if len(recipients) == 0:
                self.name = "Unnamed private group"
            else:
                self.name = ", ".join(map(lambda x: x.name, recipients))
        self.n_participants = len(chan.nicks)

    async def backfill(self, oldest_id=None, oldest_date=None):
        try:
            await self.history(oldest_date)
        except discord.errors.Forbidden:
            self.log.warning("Could not fetch history of %r", self.name)

    async def history(self, oldest: Optional[datetime] = None):
        if not config.MUC_BACK_FILL:
            return

        chan = await self.get_discord_channel()

        messages = [
            msg async for msg in chan.history(limit=config.MUC_BACK_FILL, before=oldest)
        ]
        self.log.debug("Fetched %s messages for %r", len(messages), self.name)
        for i, msg in enumerate(reversed(messages)):
            self.log.debug("Message %s", i)
            author = msg.author
            if author.id == self.session.discord.user.id:  # type:ignore
                p = await self.get_user_participant()
            else:
                try:
                    p = await self.get_participant_by_contact(
                        await self.session.contacts.by_discord_user(author)
                    )
                except XMPPError:
                    # deleted users
                    p = await self.get_participant(author.name)
            await p.send_message(msg, archive_only=True)

    async def get_participant_by_discord_user(self, user: Union[di.User, di.Member]):
        if user.discriminator == "0000":
            # a webhook, eg Github#0000
            # FIXME: avatars for contact-less participants
            p = await self.get_participant(user.display_name)
            p.DISCO_CATEGORY = "bot"
            return p
        elif user.system:
            return self.get_system_participant()
        try:
            return await self.get_participant_by_legacy_id(user.id)
        except XMPPError as e:
            self.log.warning(
                (
                    "Could not get participant with contact for %s, "
                    "falling back to a 'contact-less' participant."
                ),
                user,
                exc_info=e,
            )
            return await self.get_participant(user.display_name)

    async def create_thread(self, xmpp_id: str) -> int:
        ch = await self.get_discord_channel()
        if isinstance(ch, di.GroupChannel):
            raise XMPPError("bad-request")

        try:
            thread_id = int(xmpp_id)
        except ValueError:
            pass
        else:
            if thread_id in (t.id for t in ch.threads):
                return thread_id

        thread = await ch.create_thread(name=xmpp_id, type=di.ChannelType.public_thread)
        return thread.id
