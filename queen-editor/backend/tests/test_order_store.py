import json

from backend.features.photo_generation.data.order_store import FILE, DriveOrderStore


class FakeStorage:
    def __init__(self, texts=None):
        self.texts = dict(texts or {})

    def read_text(self, subdir, name):
        return self.texts.get((subdir, name))

    def write_text(self, subdir, name, text):
        self.texts[(subdir, name)] = text


def test_dosya_yoksa_sira_bos():
    assert DriveOrderStore(FakeStorage()).read("düğün") == []


def test_yazilan_sira_geri_okunur():
    store = DriveOrderStore(FakeStorage())
    store.write("düğün", ["1_a.png", "0_a.png"])
    assert store.read("düğün") == ["1_a.png", "0_a.png"]


def test_dosya_sadece_sirayi_tutar():
    storage = FakeStorage()
    DriveOrderStore(storage).write("düğün", ["0_a.png"])
    assert json.loads(storage.texts[("düğün", FILE)]) == {"order": ["0_a.png"]}


def test_bozuk_json_sirasiz_sayilir():
    storage = FakeStorage({("düğün", FILE): "{yarım"})
    assert DriveOrderStore(storage).read("düğün") == []


def test_beklenmedik_bicim_sirasiz_sayilir():
    storage = FakeStorage({("düğün", FILE): json.dumps({"order": "1_a.png"})})
    assert DriveOrderStore(storage).read("düğün") == []


def test_metin_olmayan_ogeler_atilir():
    storage = FakeStorage({("düğün", FILE): json.dumps({"order": ["1_a.png", 5, None]})})
    assert DriveOrderStore(storage).read("düğün") == ["1_a.png"]
