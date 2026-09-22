"""Produce videos from the project's reference pool. Returns how many jobs the queue took.

Three things stop a run before it starts (madde 302), and the app says which: the engine that can
read references is not installed, the pool is empty, or it has a hole in it. All three are the app's
to count -- H3 complains into a Colab log the user never opens, and about the last two it would not
complain at all.

Checked in the order a person would look: what is installed, then what they wrote, then what the
pool holds.

Nothing is born here yet. Cards are madde 303's, and this use case is where they will come from.
"""
from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.prompt_list import parse_prompts
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import (
    MAX_VARIANTS,
    InvalidVariants,
    ProjectMissing,
)


class NoReferenceProducer(Exception):
    """The installed video engine has no reference mode (message is user-facing)."""


def queue_references(store, pool, orders, has_h3, project, prompts, variants):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if not has_h3:
        # WAN has no such mode at all, so there is nothing to hand the pool to.
        raise NoReferenceProducer(
            "Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.")
    parse_prompts(prompts)                  # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    held = list_references(store, pool, orders, project)
    if not held:
        raise references.PoolLimit(
            "Havuzda referans yok — önce soldaki panele en az bir referans ekle.")
    open_kinds = references.gaps(held)
    if open_kinds:
        # Named, because the user is going to go and close it: H3 packs references tight and
        # numbers them by order, so a hole would point every prompt after it at the wrong file.
        said = " ve ".join(references.SAID[kind] for kind in open_kinds)
        raise references.PoolLimit(
            f"Havuzda boş yuva var ({said}) — sürükleyip kapatmadan üretim başlamaz.")
    # Nothing is born yet -- madde 303 is where the cards come from -- and the answer already
    # has the shape every other production answers in.
    return 0
