from itly.sdk import Plugin


class CustomPlugin(Plugin):
    def id(self):
        # type: () -> str
        return 'custom'
