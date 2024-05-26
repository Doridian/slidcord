from typing import TYPE_CHECKING, Optional, Union

import discord as di
import emoji
from slidge import LegacyParticipant
from slidge.core.mixins.message import ContentMessageMixin
from slidge.core.mixins.presence import PresenceMixin
from slidge.util import strip_illegal_chars
from slidge.util.types import LegacyAttachment, MessageReference

if TYPE_CHECKING:
    from .group import MUC
    from .session import Session


class MessageMixin(ContentMessageMixin):
    session: "Session"
    legacy_id: int  # type:ignore
    avatar: str
    discord_user: Union[di.User, di.ClientUser]  # type: ignore

    MARKS = False

    async def update_reactions(self, m: di.Message):
        legacy_reactions = []
        user = self.discord_user
        for r in m.reactions:
            try:
                async for u in r.users():
                    if u.id == user.id:
                        if (
                            r.is_custom_emoji()
                            or not isinstance(r.emoji, str)
                            or not emoji.is_emoji(r.emoji)
                        ):
                            legacy_reactions.append("❓")
                        else:
                            assert isinstance(r.emoji, str)
                            legacy_reactions.append(r.emoji)
            except di.NotFound:
                # the message has now been deleted
                # seems to happen quite a lot. I guess
                # there are moderation bot that are triggered
                # by reactions from users
                # oh, discord…
                return
        self.react(m.id, legacy_reactions)

    async def _reply_to(self, message: di.Message):
        if not (ref := message.reference):
            return

        quoted_msg_id = ref.message_id
        if quoted_msg_id is None:
            return

        reply_to = MessageReference(quoted_msg_id)

        try:
            if message.type == di.MessageType.thread_starter_message:
                assert isinstance(message.channel, di.Thread)
                assert isinstance(message.channel.parent, di.TextChannel)
                quoted_msg = await message.channel.parent.fetch_message(quoted_msg_id)
            else:
                quoted_msg = await message.channel.fetch_message(quoted_msg_id)
        except di.errors.NotFound:
            reply_to.body = "[quoted message could not be fetched]"
            return reply_to

        if (att := quoted_msg.attachments) and (url := att[0].url):
            reply_to.body = att[0].filename + ": " + url
        else:
            reply_to.body = quoted_msg.clean_content
        author = quoted_msg.author
        if author == self.session.discord.user:
            reply_to.author = self.session.user
            return reply_to

        muc: "MUC" = getattr(self, "muc", None)  # type: ignore
        if muc:
            reply_to.author = await muc.get_participant_by_discord_user(author)
        else:
            reply_to.author = self  # type: ignore

        return reply_to

    async def send_message(
        self, message: di.Message, archive_only=False, correction=False
    ):
        reply_to = await self._reply_to(message)

        mtype = message.type
        if mtype == di.MessageType.thread_created:
            text = f"/me created a thread named '{message.clean_content}'"
        elif mtype == di.MessageType.thread_starter_message:
            text = "I started a new thread from this message ↑"
        else:
            text = message.clean_content

        channel = message.channel
        if isinstance(channel, di.Thread):
            thread = channel.id
            if message.type == di.MessageType.channel_name_change:
                text = f"/me renamed this thread: {text}"
        else:
            thread = None

        # it seems attachments cannot be edited in discord anyway, only the text
        # of the message
        attachments = (
            [Attachment.from_discord(a) for a in message.attachments]
            if not correction
            else []
        )

        await self.send_files(
            attachments,
            body_first=True,
            legacy_msg_id=message.id,
            when=message.created_at,
            thread=thread,
            body=text,
            reply_to=reply_to,
            archive_only=archive_only,
            carbon=message.author == self.session.discord.user,
            correction=correction,
        )


class StatusMixin(PresenceMixin):
    def update_status(
        self,
        status: di.Status,
        activity: Optional[
            Union[di.Activity, di.Game, di.CustomActivity, di.Streaming, di.Spotify]
        ],
    ):
        # TODO: implement timeouts for activities (the Activity object has timestamps
        #       attached to it)
        msg = self.activity_to_text(activity)
        if status == di.Status.online:
            self.online(msg)
        elif status == di.Status.offline:
            if isinstance(self, LegacyParticipant):
                self.extended_away(msg)
            else:
                self.offline(msg)
        elif status == di.Status.idle:
            self.away(msg)
        elif status == di.Status.dnd:
            self.busy(msg)

    @staticmethod
    def activity_to_text(
        activity: Optional[
            Union[di.Activity, di.Game, di.CustomActivity, di.Streaming, di.Spotify]
        ],
    ) -> Optional[str]:
        if isinstance(activity, di.Game):
            return strip_illegal_chars(f"Playing {activity.name}")
        elif isinstance(activity, di.Streaming):
            text = f"Streaming at {activity.url}"
            if name := activity.name:
                text += f" - {name}"
            if game := activity.game:
                text += f" - {game}"
        elif isinstance(activity, di.Spotify):
            return strip_illegal_chars(
                f"Listening to {activity.title} by {activity.artist} "
                f"({activity.album}) - {activity.track_url}"
            )
        elif isinstance(activity, di.CustomActivity):
            text = ""
            if name := activity.name:
                text += name
            if e := activity.emoji:
                text += f" <{e.url}>"
            return strip_illegal_chars(text.lstrip()) or None
        elif isinstance(activity, di.Activity):
            text = ""
            if name := activity.name:
                text += name
            if state := activity.state:
                text += f" - {state}"
            if e := activity.emoji:
                text += f" <{e.url}>"
            if url := activity.large_image_url:
                text += f" - <{url}>"
            if type_ := activity.type:
                type_string = str(type_).removeprefix("ActivityType.")
                if "unknown" not in type_string:
                    text += f" - {type_string}"
            return strip_illegal_chars(text.lstrip()) or None
        return None


class Attachment(LegacyAttachment):
    @staticmethod
    def from_discord(di_attachment: di.Attachment):
        return Attachment(
            url=di_attachment.url,
            name=di_attachment.filename,
            content_type=di_attachment.content_type,
            legacy_file_id=di_attachment.id,
        )
