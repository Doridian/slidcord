DISCORD_VERBOSE = False
DISCORD_VERBOSE__DOC = (
    "Let the discord lib at the same loglevel as others loggers. "
    "By default, it's set it to WARNING because it's *really* verbose."
)

MUC_BACK_FILL = 5
MUC_BACK_FILL__DOC = (
    "The number of messages to fetch in text channels on slidge startup."
)

AUTO_FETCH_FRIENDS_BIO = False
AUTO_FETCH_FRIENDS_BIO__DOC = (
    "If set to true, slidcord will automatically fetch the 'bio' of your discord "
    "friends on startup, to push VCards4 to you. Disabled by default because of "
    "the rate limiting it triggers for some users."
)
