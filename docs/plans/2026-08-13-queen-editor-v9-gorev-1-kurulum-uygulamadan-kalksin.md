# v9 · Görev 1 — Kurulum uygulamadan kalksın (uygulama planı)

**Spec:** [2026-08-13-queen-editor-v9-gorev-1-kurulum-uygulamadan-kalksin-design.md](../specs/2026-08-13-queen-editor-v9-gorev-1-kurulum-uygulamadan-kalksin-design.md)
**Amaç:** Uygulamada indirme yapan tek satır kalmasın; panel neyin kurulu olduğunu söylemeye devam
etsin, kurulmamış olan için Colab defterini göstersin.

**Komutlar:** `python -m pytest queen-editor -q` ·
`npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

## Global kısıtlar

- Katman yönü `presentation → domain ← data → services`; somut sınıf yalnız `backend/main.py`'de.
- Kod/yorum/test adı **İngilizce**, kullanıcıya görünen metin **Türkçe**.
- **Arayüz tasarımı değişmez:** satırlar, kart ve "Kur" düğmesi yerinde kalır.
- Kullanıcıya görünen tek yeni cümle: `Bu üretici Colab defterinden kurulur — app.ipynb'yi çalıştır.`
- Ön yüz değişiyor → `dist/` aynı commit'te.
- Görev tek commit; commit mesajında çift tırnak yok.

## Sıra neden böyle

Önce testler silinip sadeleşiyor (2), sonra kod (3-5), en sonda dosyalar siliniyor (6). Tersi
olsaydı ara adımlarda takım kırmızı koşardı ve neyin gerçekten bozulduğunu göremezdik.

## Adım 1 — Kalan davranışın testini yaz (kırmızı)

**Dosya:** `backend/tests/test_producers.py`

- [ ] **1.1** Dosyayı, kurulumdan arınmış hâline getir. Kalan testler ve tek sahte:

```python
"""Which producers this machine has, and which of them are installed.

Installing is the notebook's job (FOUNDATION 9): nothing here downloads, so nothing here fakes a
download either.
"""
from backend.features.producers.domain import model_groups
from backend.features.producers.domain.usecases.list_producers import list_producers


class FakeFiles:
    def __init__(self, present=()):
        self.present = set(present)

    def exists(self, folder, name):
        return (folder, name) in self.present

    def path(self, folder, name):
        return f"/models/{folder}/{name}"


GROUPS = {
    "photo": [],
    "video": [{"folder": "vae", "name": "wan_vae.safetensors"},
              {"folder": "loras", "name": "high.safetensors"}],
    "audio": [{"folder": "mmaudio", "name": "mm.pth"}],
}


def test_all_three_are_listed_in_the_order_the_engine_works_in():
    rows = list_producers(GROUPS, FakeFiles())

    assert [row["id"] for row in rows] == ["photo", "video", "audio"]
    assert [row["name"] for row in rows] == [
        "Fotoğraf üreticisi", "Video üreticisi", "Ses üreticisi"]


def test_a_producer_with_a_group_is_installed_when_every_file_of_it_is_here():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors"), ("loras", "high.safetensors")])

    assert list_producers(GROUPS, files)[1]["installed"] is True


def test_one_missing_file_means_not_installed():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors")])

    assert list_producers(GROUPS, files)[1]["installed"] is False


def test_a_kind_with_no_group_is_not_installed():
    assert list_producers(GROUPS, FakeFiles())[0]["installed"] is False


def test_a_row_says_nothing_about_installing_because_the_app_does_not():
    row = list_producers(GROUPS, FakeFiles())[0]

    assert set(row) == {"id", "name", "installed"}


# The shipped groups: what the panel really counts has to be what the graphs really load.


def test_the_photo_group_carries_everything_the_graph_reads():
    rows = model_groups.GROUPS["photo"]

    assert [(row["folder"], row["name"]) for row in rows] == [
        ("checkpoints", "nova3DCGXL_ilV90.safetensors"),
        ("loras", "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"),
        ("upscale_models", "4x_foolhardy_Remacri.pth"),
        ("ultralytics/bbox", "face_yolov9c.pt"),
        ("sams", "sam_vit_b_01ec64.pth"),
    ]


def test_the_sound_group_names_the_weights_the_sampler_loads():
    rows = model_groups.GROUPS["audio"]

    assert len(rows) == 1, "Örnekleyici tek ağırlık dosyası yüklüyor"
    assert rows[0]["name"] == "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"


def test_the_weights_path_is_built_from_the_group_row():
    path = model_groups.audio_weights(FakeFiles())

    assert path == "/models/mmaudio/mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"


def test_no_group_carries_an_address_the_app_would_have_to_fetch():
    """Addresses live in the notebook now. One left here would be a second truth nobody reads."""
    for group in model_groups.GROUPS.values():
        for row in group:
            assert set(row) == {"folder", "name"}
```

- [ ] **1.2 Koş, kırmızıyı gör** — `python -m pytest queen-editor/backend/tests/test_producers.py -q`
      Beklenen: `test_a_row_says_nothing_about_installing…` ve `test_no_group_carries_an_address…`
      düşer (satırda `installing`/`error` alanları ve `url` anahtarları hâlâ var).

## Adım 2 — Rota testini sadeleştir (kırmızı)

**Dosya:** `backend/tests/test_producers_routes.py`

- [ ] **2.1** Dosyayı tek uca indir:

```python
"""The producers endpoint over a real Flask app, with fake models on disk."""
from backend.features.producers.data.comfy_models import ComfyModelFiles
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.presentation.routes import make_producers_blueprint
from backend.web.app import create_app

GROUPS = {"photo": [], "video": [{"folder": "vae", "name": "v.safetensors"}], "audio": []}


def make_client(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    files = ComfyModelFiles(str(tmp_path / "comfy"))
    blueprint = make_producers_blueprint(
        list_producers=lambda: list_producers(GROUPS, files))
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client()


def test_the_panel_reads_three_rows(tmp_path):
    body = make_client(tmp_path).get("/api/producers").get_json()

    assert [row["id"] for row in body["producers"]] == ["photo", "video", "audio"]
    assert body["producers"][1]["installed"] is False


def test_there_is_no_way_to_start_an_install_over_http(tmp_path):
    """The app installs nothing, so the endpoint that used to is gone rather than answering."""
    client = make_client(tmp_path)

    assert client.post("/api/producers/video/install").status_code == 404
    assert client.post("/api/producers/video/install/cancel").status_code == 404
```

- [ ] **2.2 Koş, kırmızıyı gör** — `make_producers_blueprint()` hâlâ üç argüman istiyor.

## Adım 3 — Domain'i sadeleştir

**Dosyalar:** `domain/model_groups.py`, `domain/ports.py`, `domain/usecases/list_producers.py`

- [ ] **3.1 `model_groups.py`** — `url`/`auth` alanları, `CIVITAI*` sabitleri, `civitai_headers` ve
      `LIBRARIES` silinir; `HF_WAN21`/`HF_WAN22` de gider (yalnız adres kuruyorlardı). Kalan:
      üç grup (yalnız `folder` + `name`), `HF_MMAUDIO_NSFW` ve `audio_weights`. Modül docstring'i
      yeniden yazılır: bu bir **okuma** listesi, adresler defterde.

- [ ] **3.2 `ports.py`** — yalnız `ModelFiles` (`exists`, `path`). `Fetcher`, `Libraries` ve
      `remove` gider; `remove`'u kimse çağırmıyor ve silme diye bir iş yok.

- [ ] **3.3 `list_producers.py`** — imza `list_producers(groups, files)`. `running`, `installing`,
      `error` ve kütüphane kontrolü gider. Docstring: kurulu olmak = grubun her dosyası diskte;
      grubu boş olan kurulu değil.

- [ ] **3.4 Koş** — `python -m pytest queen-editor/backend/tests/test_producers.py -q` yeşil.

## Adım 4 — Rotayı ve bağlamayı sadeleştir

**Dosyalar:** `presentation/routes.py`, `backend/config.py`, `backend/main.py`

- [ ] **4.1 `routes.py`** — `make_producers_blueprint(list_producers)`; iki POST ucu ve `Busy`
      alımı silinir. GET'in hata yakalaması kalır (panel üç satırı veremezse kendi cümlesini basar).

- [ ] **4.2 `config.py`** — `CIVITAI_COOKIE` ve `LIB_ROOT` silinir. `COMFY_ROOT` kalır: panel
      dosyalara oradan bakıyor.

- [ ] **4.3 `main.py`** — `HttpFetcher`, `InstallRunner`, `PipLibraries`, `install_producer`,
      `cancel_install`, `civitai_headers`, `CIVITAI`, `LIBRARIES`, `_auth` içe aktarımları ve
      kurulumları silinir. Kalan bağlama:

```python
_producers_bp = make_producers_blueprint(
    list_producers=lambda: list_producers(GROUPS, _model_files))
```

- [ ] **4.4 Koş** — `python -m pytest queen-editor -q`

## Adım 5 — Ön yüz: düğme kalır, işi değişir

**Dosyalar:** `features/producers/InstallCard.jsx`, `ProducersPanel.jsx`, `useProducers.js`,
`shared/api.js` ve testleri

- [ ] **5.1 Testleri yaz (kırmızı)** — `InstallCard.test.jsx`'te kurulum akışı testleri yerine:

```jsx
  it("sends nothing to the server and says where the install happens", () => {
    const onInstall = vi.fn();
    render(<InstallCard producer={MISSING} onInstall={onInstall} />);

    fireEvent.click(screen.getByText("Kur"));

    expect(screen.getByText(
      "Bu üretici Colab defterinden kurulur — app.ipynb'yi çalıştır.")).toBeTruthy();
    expect(onInstall).not.toHaveBeenCalled();
  });
```

`ProducersPanel.test.jsx`'te aynısı satır için; "kuruluyor…", "İptal" ve onay penceresi testleri
silinir. `useProducers.test.jsx` tamamen silinir — iyimser kurulum ve geri alma diye bir şey kalmadı.

- [ ] **5.2 Koş, kırmızıyı gör** — `npm test --prefix queen-editor/frontend -- --run`

- [ ] **5.3 Bileşenleri yaz** — `Running` bileşeni, `installing`/`error` dalları, `onCancel`,
      `ConfirmModal` kullanımı ve `onInstall` prop'u gider. Düğme yerinde kalır; tıklayınca kendi
      içinde bir bayrak açar ve cümleyi bugünkü hata satırının yerinde gösterir.

- [ ] **5.4 `useProducers.js`** — yalnız listeleme kalır: bir kez okur, yoklamaz.
      `install`, `cancel`, `said`, `POLL_MS` ve zamanlayıcı gider.

- [ ] **5.5 `shared/api.js`** — `installProducer` ve `cancelInstall` silinir; testinden de.

- [ ] **5.6 Çağrı yerleri** — `ProjectScreen.jsx`, `GeneratePanel.jsx`, `LayerPanel.jsx`,
      `SidePanel.jsx` içinde kurulumla ilgili prop ve "kuruluyor" göstergesi kalmasın.

- [ ] **5.7 Koş, yeşil + derle** — `npm test … --run`, sonra `npm run build …`

## Adım 6 — Ölen dosyaları sil

- [ ] **6.1** `backend/services/download/` (klasör), `backend/features/producers/runner.py`,
      `domain/usecases/install_producer.py`, `domain/usecases/cancel_install.py`,
      `data/pip_libraries.py`, `tests/test_fetcher.py`,
      `tests/test_model_install_is_the_apps_job.py`

- [ ] **6.2 Koş** — `python -m pytest queen-editor -q`; artakalan bir içe aktarım varsa burada
      patlar.

## Adım 7 — Belgeler

- [ ] **7.1 `FOUNDATION.md` madde 9** tersine yazılır: kurulum defterin işi, uygulama yalnız ne
      olduğunu söyler. Gerekçesi de yazılır — uygulamanın indiricisi kapılı kaynakta çalışmadı,
      kanıtlanmış hücre çalışıyor.
- [ ] **7.2 `CODE-STANDARD.md`** — devralma tablosundaki model satırı: adları uygulama tutar,
      adresleri ve indirme makinesini defter.
- [ ] **7.3 `CLAUDE.md`** — "notebook installs code" paragrafı ve v9 işareti.
- [ ] **7.4 `README.md`** — kurulumun defterde olduğunu söyler; "uygulama kendi üreticilerini
      kurar" cümlesi kalkar.

## Adım 8 — Kapanış

- [ ] **8.1** İki takım da yeşil, `dist/` derlenmiş.
- [ ] **8.2 Commit** — kod + testler + `dist/` + belgeler + spec + plan + roadmap.

## Kendi kontrolüm

- Görev 2 daha yapılmadığı için, bu commit'ten sonra **hiçbir model kurulamaz**. Ara durum bilerek:
  kullanıcı "önce sil, sonra deftere koy" dedi ve iki adımı ayrı istedi. ✓
- Ses kütüphanesi de kurulamaz hâle geliyor (v8'de defterden çıkmıştı, şimdi uygulamadan da
  çıkıyor). Kullanıcının kararı "şimdilik yalnız fotoğraf"; video ve sesin kurulumu sonraki koşuda. ✓
- `ComfyModelFiles.remove` artık kimsenin çağırmadığı bir metot: portla birlikte o da siliniyor. ✓
- `test_model_install_is_the_apps_job.py` siliniyor çünkü koruduğu kural tersine döndü — bırakılsa
  Görev 2'de kırmızı yanardı ve yanlış yerde bir tartışma açardı. ✓
