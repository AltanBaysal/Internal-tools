"""OrderStore over DriveStorage -- the only place that knows the order file's name and shape.

Unreadable is not an error: a missing, half-written or hand-edited file means "no manual order",
and the gallery falls back to the record's own sequence. A project must never fail to open because
of the file that only decides sequence.
"""
import json

FILE = "order.json"


class DriveOrderStore:
    def __init__(self, storage):
        self._storage = storage

    def read(self, project):
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return []
        try:
            data = json.loads(raw)
        except ValueError:
            return []
        if not isinstance(data, dict):
            return []
        order = data.get("order")
        if not isinstance(order, list):
            return []
        return [name for name in order if isinstance(name, str)]

    def write(self, project, order):
        self._storage.write_text(
            project, FILE, json.dumps({"order": order}, ensure_ascii=False, indent=2))
