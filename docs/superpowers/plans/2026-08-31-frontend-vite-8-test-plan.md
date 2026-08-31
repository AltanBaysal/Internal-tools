# Ön yüz vite 8 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-31-frontend-vite-8-testler-design.md](../specs/2026-08-31-frontend-vite-8-testler-design.md)
**Dal:** `feat/frontend-vite-8` *(`main`'den açıldı; Madde 137 kendi dalında ve bu işi beklemiyor)*
**Bu tur yalnız test dosyalarına dokunur.** `package.json` bu turda **değişmez** — değişse kırmızı
diye bir şey kalmazdı.
**Test komutları (değişmez, dördü de — iş iki araca da dokunuyor):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## 0. Önce queen-editor'ün bağımlılıkları kurulur, ve bu bir ölçüm.

```
npm install --prefix queen-editor/frontend
```

O ön yüzün `node_modules`'ü bu cihazda hiç kurulmadı, yani dört komuttan biri bugün koşamıyor.
Kurulum bugünkü `package.json`'ı okuyacağı için **vite 5** iner — ve bu bilerek: uygulama turundan
*önce* o testlerin yeşil olduğunu görmek gerekiyor. Görülmezse, yükseltmeden sonra çıkan bir
kırmızının vite 8'den mi yoksa öteden beri mi kırık olduğu söylenemez.

Uygulama turu aynı klasöre vite 8'i kuracak; bu kurulum bir taban ölçümü, boşa giden bir adım değil.

## A. `queen-agent/backend/tests/test_frontend_toolchain.py` — yeni dosya, üç kırmızı.

Deseni `test_dist_is_committed.py`'den: bir alt sistemi değil **manifestoyu** inceleyen, ama
`pytest` onu oradan topladığı için backend'in test klasöründe duran Python testi. Hata mesajları
Türkçe, o dosyadaki gibi.

```python
"""The frontend's build chain is pinned here, and the pin is read off package.json.

This file sits beside the backend's tests because `pytest queen-agent` collects them from here, but
what it examines is the frontend's manifest -- the same reason test_dist_is_committed.py lives here.

Why the versions are guarded at all: the three move together or not at all. vitest carries vite as
a direct dependency rather than a peer, so a tree where they disagree does not fail to install --
it quietly runs the tests on one engine and builds on another. Nothing in npm says that is wrong,
so a test does.

The major is read rather than the whole range: the decision is "vite 8", not the string it was
first written as, and a patch bump must not have to edit a test to stay true.
"""
import json
import os

PACKAGE = os.path.join(
    os.path.dirname(          # queen-agent
        os.path.dirname(      # backend
            os.path.dirname(os.path.abspath(__file__)))),  # tests
    "frontend",
    "package.json",
)


def _declared():
    with open(PACKAGE, encoding="utf-8") as handle:
        return json.load(handle)["devDependencies"]


def _major(spec):
    """The major version a range allows: "^8.0.0" -> 8."""
    return int(spec.lstrip("^~>=< ").split(".")[0])


def test_the_frontend_builds_with_vite_eight():
    # GHSA-67mh-4wv8-2f99: vite 5 carries esbuild <=0.24.2, whose dev server answers any origin and
    # hands back source. Closed from vite 6.2 on; 8 was chosen because it costs no source change.
    assert _major(_declared()["vite"]) == 8, "vite 8 bekleniyordu — güvenlik açığı vite 5'te"


def test_the_react_plugin_matches_that_vite():
    # @vitejs/plugin-react 6 declares vite ^8.0.0 and nothing else, so this is not a free choice.
    assert _major(_declared()["@vitejs/plugin-react"]) == 6, (
        "plugin-react 6 bekleniyordu — 6 yalnız vite ^8 kabul ediyor"
    )


def test_the_test_runner_rides_the_same_vite():
    # vitest 3 depends on vite ^5 || ^6 || ^7 directly. Left at 3, it would install its own vite 7
    # beside the project's 8, and the suite would measure a build nobody ships.
    assert _major(_declared()["vitest"]) == 4, (
        "vitest 4 bekleniyordu — vitest 3 kendi vite 7'sini kurar ve testler başka motorda koşar"
    )
```

## B. `queen-editor/backend/tests/test_frontend_toolchain.py` — aynı dosya, üç kırmızı daha.

Birebir aynı içerik; tek fark `PACKAGE`'ın `queen-editor/frontend/package.json`'a çözülmesi, ki
yollar `__file__`'dan türediği için **metin de aynı kalıyor**. Kopya bilerek: iki araç ayrı
`pytest` koşusu, ve ortak bir yardımcı dosya birini ötekinin klasörüne bağımlı kılardı.

## C. Koşuldu: **6 kırmızı** *(her araçta üç)*, taban tertemiz.

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-agent -q` | **3 kırmızı**, 647 yeşil |
| `python -m pytest queen-editor -q` | **3 kırmızı**, 715 yeşil |
| `npm test --prefix queen-agent/frontend` | 568 yeşil |
| `npm test --prefix queen-editor/frontend` | 584 yeşil |

Altısı da gerçek `AssertionError` — bir adın yokluğu değil, bugünkü sürümün kendisi:
`assert 5 == 8`, `assert 4 == 6`, `assert 3 == 4`. **Taban ölçümü amacına ulaştı:** iki ön yüz
takımı da yükseltmeden önce tamamen yeşil, yani sonradan çıkacak her kırmızı vite 8'in.

### Yolda çıkan, bu maddenin olmayan bir eksik

`pytest queen-editor` ilk koşuda hiç başlayamadı: `ModuleNotFoundError: No module named 'requests'`.
`backend/services/comfy/client.py` ile `backend/services/xai/client.py` `requests` kullanıyor, ama
[queen-editor/backend/requirements.txt](../../../queen-editor/backend/requirements.txt) yalnız
`flask` ve `pytest` sayıyor. Dosya eksik bir liste veriyor, ve bu ancak sıfırdan kurulan bir cihazda
görünüyor — 31 Ağustos'ta ilk kez oldu.

Koşu ilerlesin diye `requests` elle kuruldu. **Dosya bu turda düzeltilmedi:** bu maddenin işi değil
ve bir yükseltme turunun içine ilgisiz bir düzeltme sıkıştırmak, kırmızının nereden geldiğini
bulanıklaştırır. Kendi maddesi olmayı bekliyor.

## D. Kırmızı commit.

## Bilerek yapılmayanlar

`skip`/`xfail` yok. `package.json` ellenmez. `vite.config.js` ellenmez. `dist` derlenmez. Mevcut ön
yüz testlerine dokunulmaz — onlar bu işin güvenlik ağı, ve ağı işle birlikte değiştirmek ağı
kaldırmaktır.
