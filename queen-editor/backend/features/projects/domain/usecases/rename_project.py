"""Give one project a new name -- the folder's own name, because that is what a project is.

Everything a project knows lives inside its folder: the plan, the record, the settings, the exports.
All of it travels with the move and none of it is rewritten, and frame names were never the
project's name to begin with.

`move` is where a running production is carried over (photo_generation's own use case). What is
behind it is not this feature's business, the same way `halt` is not.

Both exception messages are user-facing Turkish and they are the ones creating a project already
uses: one situation, one sentence, whichever window the user is in.
"""
from backend.features.projects.domain import name_rules
from backend.features.projects.domain.usecases.create_project import InvalidName, NameTaken
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def rename_project(store, move, old, new):
    error = name_rules.validate(new)
    if error:
        raise InvalidName(error)
    # A project saved under the name it already has is not a mistake, and there is nothing to move.
    if new == old:
        return
    answer = move(old, new, lambda: store.rename(old, new))
    # `is` and not truthiness: the two failures are two different sentences and neither is falsy by
    # accident.
    if answer is None:
        raise NameTaken("Bu ad zaten kullanılıyor. Başka bir ad dene.")
    if answer is False:
        raise ProjectMissing(f"Proje yok: {old}")
