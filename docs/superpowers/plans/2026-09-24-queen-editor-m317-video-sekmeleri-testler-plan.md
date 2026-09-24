# Madde 317 — Video panelinin iki sekmesi, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in 24 testi ve iki değişikliği — kırmızı.

**Yaklaşım:** Sunucuda yeni bir dosyada deposu, kullanım durumu ve kapısıyla Referanstan'ın kaydı;
ekranda LayerPanel'in sekmeleri ve taslağı. Yeni modüller testlerin içinde import ediliyor, çünkü bu
turda yoklar. LayerPanel'in testinde `api.js`'in iki yeni fonksiyonu sahte, geri kalanı gerçek.

**Spec:** [m317 test turu](../specs/2026-09-24-queen-editor-m317-video-sekmeleri-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; arayüz metni tasarımdan harfi harfine.
- Testler dört satırla koşulur; `skip` / `xfail` / `.skip` / `.todo` yok. Bu turda kaynak kod
  değişmiyor.
- **Karar, yazılsın diye:** yolda olan kayıt, kutulardan **herhangi birine** yazılmışsa hiçbirini
  doldurmuyor — kutular tek bir taslak, yarısı kayıttan yarısı elden bir karışım olmuyor.

---

## Görev 1: Sunucu — `backend/tests/test_reference_settings.py` *(yeni)*

```python
"""Referanstan's own record: what its boxes open with once the visit's draft is gone (madde 317).

The photo panel's settings.json is written when a photo batch is sent and this one when a reference
production is, so each keeps a file of its own (CODE-STANDARD, Separation of concerns).

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
from functools import partial

import pytest

from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.get_settings import ProjectMissing, get_settings
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

EMPTY = {"prompts": "", "variants": None}
URL = "/api/projects/düğün/reference-settings"


def store_at(path):
    from backend.features.projects.data.reference_settings_store import (
        DriveReferenceSettingsStore,
    )
    return DriveReferenceSettingsStore(DriveStorage(str(path)))


def save(*args):
    from backend.features.projects.domain.usecases.save_reference_settings import (
        save_reference_settings,
    )
    return save_reference_settings(*args)


def test_a_record_never_written_reads_empty(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_what_is_written_reads_back_as_it_was_typed(tmp_path):
    # The box reopens looking the way it was left: a parsed list would come back reformatted.
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    typed = '[\n  "gotik kız",\n]'
    store.write("düğün", {"prompts": typed, "variants": 3})
    assert store.read("düğün") == {"prompts": typed, "variants": 3}


@pytest.mark.parametrize("raw", ["{ yarım", "[]", '{"prompts": 5, "variants": true}',
                                 '{"prompts": null, "variants": "4"}'])
def test_an_unreadable_record_reads_empty(tmp_path, raw):
    # The record only refills boxes: what cannot be read must not keep the tab from opening.
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "reference_settings.json").write_text(raw, encoding="utf-8")
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_the_record_keeps_a_file_of_its_own(tmp_path):
    (tmp_path / "düğün").mkdir()
    store_at(tmp_path).write("düğün", {"prompts": '["a"]', "variants": 2})
    assert (tmp_path / "düğün" / "reference_settings.json").exists()
    assert not (tmp_path / "düğün" / "settings.json").exists()
    assert DriveSettingsStore(DriveStorage(str(tmp_path))).read("düğün")["prompts"] == ""


class FakeStore:
    def __init__(self):
        self.saved = {}

    def project_exists(self, project):
        return project == "düğün"

    def write(self, project, settings):
        self.saved[project] = settings


def test_saving_stores_what_it_was_given():
    store = FakeStore()
    save(store, "düğün", '["a"]', 3)
    assert store.saved == {"düğün": {"prompts": '["a"]', "variants": 3}}


def test_saving_refuses_a_project_that_is_not_there():
    store = FakeStore()
    with pytest.raises(ProjectMissing) as exc:
        save(store, "yok", '["a"]', 3)
    assert str(exc.value) == "Proje yok: yok"
    assert store.saved == {}


def make_client(tmp_path):
    """The door wired by hand over a temp folder -- the wiring main.py does."""
    from backend.features.projects.data.reference_settings_store import (
        DriveReferenceSettingsStore,
    )
    from backend.features.projects.domain.usecases.save_reference_settings import (
        save_reference_settings,
    )
    from backend.features.projects.presentation.reference_settings_routes import (
        make_reference_settings_blueprint,
    )
    drive = tmp_path / "drive"
    drive.mkdir()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    store = DriveReferenceSettingsStore(DriveStorage(str(drive)))
    blueprint = make_reference_settings_blueprint(
        get_reference_settings=partial(get_settings, store),
        save_reference_settings=partial(save_reference_settings, store))
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client(), drive


def test_a_new_project_answers_with_an_empty_record(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün").mkdir()
    assert client.get(URL).get_json() == EMPTY


def test_a_record_put_down_comes_back(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün").mkdir()
    resp = client.put(URL, json={"prompts": '["a"]', "variants": 3})
    assert resp.status_code == 204
    assert client.get(URL).get_json() == {"prompts": '["a"]', "variants": 3}


def test_an_unknown_project_is_a_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/reference-settings").status_code == 404
    assert client.put("/api/projects/yok/reference-settings",
                      json={"prompts": "x", "variants": 1}).status_code == 404


def test_a_put_never_creates_a_project(tmp_path):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client, drive = make_client(tmp_path)
    client.put("/api/projects/yok/reference-settings", json={"prompts": "x", "variants": 1})
    assert not (drive / "yok").exists()


@pytest.mark.parametrize("variants", [True, "4", 2.5, None])
def test_fields_of_the_wrong_type_are_stored_empty(tmp_path, variants):
    # bool is an int in Python, and True would silently mean "1 variant".
    client, drive = make_client(tmp_path)
    (drive / "düğün").mkdir()
    client.put(URL, json={"prompts": 5, "variants": variants})
    assert client.get(URL).get_json() == EMPTY
```

## Görev 2: Sunucu — `backend/tests/test_composition_root.py`

Dosyanın sonuna:

```python
@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_referanstans_record(import_main, video_model):
    """Madde 317: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m317-yok/reference-settings")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m317-yok"}
```

## Görev 3: Ekran — `frontend/src/shared/api.test.js`

`carries the production mode into the queue request`'in hemen altına:

```js
  it("reads and writes Referanstan's record at the project's own address", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ prompts: "", variants: null }));
    vi.stubGlobal("fetch", fetchMock);

    // Through the module, so a missing export fails this test rather than the file.
    await api.getReferenceSettings("düğün");
    await api.saveReferenceSettings("düğün", { prompts: '["a"]', variants: 2 });

    const url = `/api/projects/${encodeURIComponent("düğün")}/reference-settings`;
    expect(fetchMock.mock.calls[0][0]).toBe(url);
    expect(fetchMock.mock.calls[0][1].method).toBeUndefined();
    const [putUrl, put] = fetchMock.mock.calls[1];
    expect(putUrl).toBe(url);
    expect(put.method).toBe("PUT");
    expect(JSON.parse(put.body)).toEqual({ prompts: '["a"]', variants: 2 });
  });
```

## Görev 4: Ekran — `frontend/src/features/photo_generation/LayerPanel.test.jsx`

- [ ] **Adım 1: Başlık.** İmportlar ve sahte `api.js`:

```jsx
import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getReferenceSettings, saveReferenceSettings } from "../../shared/api.js";
import LayerPanel from "./LayerPanel.jsx";

// Referanstan's record is the server's; everything else the panel needs arrives as props.
vi.mock("../../shared/api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  getReferenceSettings: vi.fn(),
  saveReferenceSettings: vi.fn(),
}));
```

- [ ] **Adım 2: `renderPanel`'in önüne ve içine.**

```jsx
// Referanstan's draft is kept per project for the length of a visit, in the module. A name of its
// own for every render keeps one test's typing out of the next one's panel.
let rendered = 0;
const freshProject = () => `proje-${++rendered}`;

beforeEach(() => {
  vi.clearAllMocks();
  getReferenceSettings.mockResolvedValue({ prompts: "", variants: null });
  saveReferenceSettings.mockResolvedValue(null);
});

const tab = (name) => screen.getByRole("button", { name });
const labels = (view) => [...view.container.querySelectorAll("[data-label]")]
  .map((one) => one.textContent);

function renderPanel(props) {
  return render(
    <LayerPanel layer="video" project={freshProject()} frames={FRAMES} selected={[]}
                producer={null} onQueue={() => Promise.resolve({ added: 2 })}
                onInstall={() => {}} {...props} />,
  );
}
```

- [ ] **Adım 3: Değişen test** — `asks the video panel where the video comes from, and never the sound
  panel`'in ilk yarısı:

```jsx
    renderPanel();
    // Kareden, not Standart: Standart already names a mode on the Kareden tab itself.
    expect(screen.getByText("Kareden")).toBeTruthy();
    expect(screen.getByText("Referanstan")).toBeTruthy();
```

- [ ] **Adım 4: Yeni iki blok, dosyanın sonuna.**

```jsx
describe("LayerPanel — the two tabs", () => {
  it("opens the video panel on Kareden, with the frame form", () => {
    const view = renderPanel();

    expect(tab("Kareden").className).toContain("is-on");
    expect(tab("Referanstan").className).not.toContain("is-on");
    expect(labels(view)).toEqual(["Model", "Kapsam", "Üretim modu", "Varyant"]);
    // The row the tabs replace, and its old word for the frame side.
    expect(screen.queryByText("Üretim")).toBeNull();
    expect(screen.queryByText("Karelerden")).toBeNull();
  });

  it("lays Referanstan out in the design's order", () => {
    const view = renderPanel();

    fireEvent.click(tab("Referanstan"));

    expect(tab("Referanstan").className).toContain("is-on");
    expect(tab("Kareden").className).not.toContain("is-on");
    expect(labels(view)).toEqual(["Model", "Referanslar", "Prompt listesi", "Varyant"]);
  });

  it("gives the sound panel no tabs", () => {
    // A sound is laid over a video that already exists: the pool has nothing to give it.
    renderPanel({ layer: "audio" });

    expect(screen.queryByText("Kareden")).toBeNull();
    expect(screen.queryByText("Referanstan")).toBeNull();
  });
});

describe("LayerPanel — what Referanstan keeps", () => {
  const promptBox = () => screen.getByLabelText("Prompt listesi");

  it("keeps its prompt list and variants across the tabs, and Kareden keeps its own one", () => {
    renderPanel();
    fireEvent.click(tab("Referanstan"));
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    fireEvent.click(tab("Kareden"));
    // Kareden is the frame form as it was: its count starts at one on every opening.
    expect(variantBox().value).toBe("1");

    fireEvent.click(tab("Referanstan"));
    expect(promptBox().value).toBe('["gotik kız"]');
    expect(variantBox().value).toBe("3");
  });

  it("keeps them when the panel is built again, which opens on Kareden", async () => {
    // Opening the panel from the rail, or stepping into a frame and back, builds it afresh.
    const first = renderPanel({ project: "düğün-a" });
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });
    first.unmount();

    renderPanel({ project: "düğün-a" });

    expect(tab("Kareden").className).toContain("is-on");
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(promptBox().value).toBe('["gotik kız"]');
    expect(variantBox().value).toBe("3");
    // A draft is newer than the record by definition, so the record is asked once per visit.
    expect(getReferenceSettings).toHaveBeenCalledTimes(1);
  });

  it("fills the boxes from the project's record when nothing was typed this visit", async () => {
    getReferenceSettings.mockResolvedValue({ prompts: '["kayıt"]', variants: 4 });
    renderPanel({ project: "düğün-b" });

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    expect(getReferenceSettings).toHaveBeenCalledWith("düğün-b");
    expect(promptBox().value).toBe('["kayıt"]');
    expect(variantBox().value).toBe("4");
  });

  it("opens Referanstan on one variant when the record has none", async () => {
    renderPanel({ project: "düğün-c" });

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    expect(getReferenceSettings).toHaveBeenCalledWith("düğün-c");
    expect(variantBox().value).toBe("1");
  });

  it("does not write the record over what was typed while it was on its way", async () => {
    let answer;
    getReferenceSettings.mockReturnValue(new Promise((resolve) => { answer = resolve; }));
    renderPanel({ project: "düğün-d" });
    fireEvent.click(tab("Referanstan"));
    fireEvent.change(promptBox(), { target: { value: '["yeni"]' } });

    await act(async () => { answer({ prompts: '["eski"]', variants: 5 }); });

    expect(getReferenceSettings).toHaveBeenCalledWith("düğün-d");
    // Neither box: a draft is one thing, never half the record and half the hand.
    expect(promptBox().value).toBe('["yeni"]');
    expect(variantBox().value).toBe("1");
  });

  it("writes the record first when the press goes out, then sends the work", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 3 });
    renderPanel({ project: "düğün-e", onQueue });
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(saveReferenceSettings).toHaveBeenCalledWith(
      "düğün-e", { prompts: '["gotik kız"]', variants: 3 });
    expect(onQueue).toHaveBeenCalledWith(null, 3, "reference", '["gotik kız"]');
    expect(saveReferenceSettings.mock.invocationCallOrder[0])
      .toBeLessThan(onQueue.mock.invocationCallOrder[0]);

    // Kareden's press is about frames: it writes no reference record.
    fireEvent.click(tab("Kareden"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });
    expect(saveReferenceSettings).toHaveBeenCalledTimes(1);
  });

  it("sends nothing when the record cannot be written", async () => {
    // The photo panel's rule: the record and the work land in the same folder, so a record that
    // cannot be written means the work could not be either.
    saveReferenceSettings.mockRejectedValue(new Error("Proje yok: düğün-g"));
    const onQueue = vi.fn();
    renderPanel({ project: "düğün-g", onQueue });
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).not.toHaveBeenCalled();
    expect(screen.getByText("Proje yok: düğün-g")).toBeTruthy();
  });
});
```

## Görev 5: Ekran — `frontend/src/features/photo_generation/SidePanel.test.jsx`

- [ ] **Adım 1: Sahte sunucu**, `renderColumn`'un altına:

```jsx
// Referanstan's record the way the server answers it: an empty one to read, nothing back for a
// write.
function recordServer() {
  const answer = (text) => ({ ok: true, status: 200, statusText: "OK", text: async () => text });
  return vi.fn((path, options) => Promise.resolve(answer(
    options?.method === "PUT" ? "" : JSON.stringify({ prompts: "", variants: null }))));
}
```

- [ ] **Adım 2: Değişen test** — `passes the reference prompt list through to the queue`'nun ilk
  satırı:

```jsx
    // The press writes Referanstan's record before it sends the work (madde 317).
    vi.stubGlobal("fetch", recordServer());
```

- [ ] **Adım 3: Yeni test**, onun altına:

```jsx
  it("opens the video panel on Kareden again, with Referanstan's words still there", async () => {
    vi.stubGlobal("fetch", recordServer());
    renderColumn({ frames: [] });

    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(screen.getByText("Referanstan")); });
    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız"]' } });
    // Closed and opened again from the rail: the panel is built afresh.
    fireEvent.click(screen.getByLabelText("Video üret"));
    fireEvent.click(screen.getByLabelText("Video üret"));

    expect(screen.getByRole("button", { name: "Kareden" }).className).toContain("is-on");
    fireEvent.click(screen.getByRole("button", { name: "Referanstan" }));
    expect(screen.getByLabelText("Prompt listesi").value).toBe('["gotik kız"]');
  });
```

## Görev 6: Koşu ve kırmızı commit

- [ ] **Adım 1: Dört satırı koş** — `queen-editor` pytest'te yalnız Görev 1 ve 2; vitest'te Görev 3,
  4 *(`gives the sound panel no tabs` hariç)* ve 5'in yeni testi ile Görev 4'ün değişen testi kırmızı.
  `queen-agent` iki satırı yeşil.
- [ ] **Adım 2: Kırmızı commit** — testler, spec ve bu plan: `test(m317): …(red)`.
