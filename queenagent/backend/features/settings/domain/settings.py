"""Settings -- what the app was told about itself, as opposed to what the user made in it.

Its own feature rather than a corner of the workspace: no project, chat or file touches the key, and
the workspace never imports this. What binds the two is the composition root, whose job that is.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Empty is the ordinary starting state: the app runs without a key and only asking for an answer
    # fails. Saving an empty one is also how a key is taken back out.
    api_key: str = ""
