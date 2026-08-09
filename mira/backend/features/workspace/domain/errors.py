"""Errors the workspace domain raises. The routes are what turn them into status codes."""


class ProjectNotFound(Exception):
    """No project carries this id."""


class InvalidProjectName(Exception):
    """A project cannot be left without a name."""


class EmptyMessage(Exception):
    """A message with nothing in it does not start a chat."""


class ChatNotFound(Exception):
    """No chat carries this id inside that project."""


class EngineFailed(Exception):
    """The engine could not answer. Carries the engine's own words."""


class FileNotFound(Exception):
    """The project holds no file by this name."""


class NameTaken(Exception):
    """Something already answers to that name, and nothing is ever overwritten."""
