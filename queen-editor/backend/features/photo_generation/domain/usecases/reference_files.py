"""The project's reference pool as files, in the order H3 will number them.

Read when a job's turn comes rather than written into its plan line: the user's own call is that a
retry produces with the pool as it stands now, and a card does not remember what it was made from
(roadmap decision, 21 Eylül).

The order is the pool's own -- the one the user dragged (madde 300) -- because H3 numbers references
by order and the prompt's <Picture 2> counts from there.
"""
from backend.features.photo_generation.domain.usecases.list_references import list_references


def reference_files(store, pool, orders, project):
    """[(name, bytes, kind)] -- empty when the project has no pool at all."""
    return [(row["name"], pool.read(project, row["name"]), row["kind"])
            for row in list_references(store, pool, orders, project)]
