"""Errors the workspace domain raises. The routes are what turn them into status codes."""


class ProjectNotFound(Exception):
    """No project carries this id."""


class InvalidProjectName(Exception):
    """A project cannot be left without a name."""


class EmptyMessage(Exception):
    """A message with nothing in it does not start a chat."""


class ChatNotFound(Exception):
    """No chat carries this id inside that project."""


class ChatNotFull(Exception):
    """Only a full chat is trimmed."""


class ChatFull(Exception):
    """The chat has reached its context ceiling and takes no further turn."""


class NothingToAnswer(Exception):
    """No sentence and no chat waiting: the request asks for nothing."""


class VersionNotFound(Exception):
    """The chat has no version of this name."""


class UnknownMode(Exception):
    """No mode goes by this name (Madde 463): nothing is written for it."""


class ChatHeld(Exception):
    """A turn holds this chat (Madde 461): one is answering in it, or its record is being written."""


class ProjectAnswering(Exception):
    """A chat of this project has a turn running, so the project cannot move to the trash."""


class EngineFailed(Exception):
    """The engine could not answer. Carries the engine's own words."""


class FileNotFound(Exception):
    """The project holds no file by this name."""


class BadStructure(Exception):
    """No prompts can be built from this file. Carries what is wrong, in words."""
