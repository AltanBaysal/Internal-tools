"""The order the user dragged the reference pool into -- the only place that knows this file.

A document of its own beside the folder, because it answers what the folder cannot: which slot each
reference stands in (madde 300). The folder says what exists; this says in what order. A name can
outlive its file here -- one deleted by hand in Drive -- and it then stands in no slot (madde 321).

Unreadable is not an error: a missing, half-written or hand-edited file means "no order", and the
pool falls back to reading by name. A project must never fail to open because of the file that only
decides sequence -- the rule DriveOrderStore already follows for the gallery.
"""
import json

FILE = "references.json"


class DriveReferenceOrderStore:
    def __init__(self, storage):
        self._storage = storage

    def read(self, project):
        """{kind: [name, …]} -- empty when there is nothing readable to go on."""
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return {}
        try:
            data = json.loads(raw)
        except ValueError:
            return {}
        if not isinstance(data, dict):
            return {}
        return {kind: [name for name in names if isinstance(name, str)]
                for kind, names in data.items() if isinstance(names, list)}

    def write(self, project, order):
        self._storage.write_text(
            project, FILE, json.dumps(order, ensure_ascii=False, indent=2))
