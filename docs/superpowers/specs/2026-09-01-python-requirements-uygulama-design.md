# Python bağımlılıkları dosyada durur · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-01-python-requirements-testler-design.md](2026-09-01-python-requirements-testler-design.md)
**Kırmızı commit:** `a52fca1` — 3 kırmızı, geri kalan yeşil.
**Dal:** `feat/python-requirements`.

## Ne yeşile dönecek

Üç bekçi, iki dosyayla.

### 1. `queen-editor/backend/requirements.txt` bir satır alır

```
flask>=3.0
pytest>=8.0
requests>=2.32
```

`requests` bu iki dosyada modül düzeyinde içe aktarılıyor:
[services/comfy/client.py](../../../queen-editor/backend/services/comfy/client.py) ve
[services/xai/client.py](../../../queen-editor/backend/services/xai/client.py).

**Taban, tavan değil** — dosyanın öteki iki satırıyla aynı biçim. Sürüm sabitlemiyor, çok eskisini
dışarıda bırakıyor. Cihazda kurulu olan 2.34.2 bu tabanı karşılıyor.

### 2. `queen-agent/backend/requirements.txt` doğar

```
flask>=3.0
pytest>=8.0
```

İkisi de yeter, ve bu bir tahmin değil: aracın backend'inde modül düzeyinde içe aktarılan üçüncü
parti isim yalnız bu ikisi — `flask` uygulamanın, `pytest` testlerinin. Bekçi zaten bunu ölçüyor,
yani eksik bir satır kırmızıda görünür.

Sürümler queen-editor'ünkiyle aynı. İki araç aynı Python'da koşuyor ve farklı tabanlar yazmak, bir
sebebi olmadan iki gerçek yaratırdı.

**Bu dosya bugüne kadar yoktu, ve yokluğu bir eksiklikti.** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md)
`flask`'ın tek bağımlılık olduğunu söylüyor — doğru söylüyor, ama `pip` cümle okumuyor. Doküman
kuralı da bunu istiyor: *"A doc says what the code cannot."* Kurulacak paketlerin listesi kodun
söyleyebileceği bir şey, ve artık söylüyor.

## Değişmeyen

`torch`, `torchaudio`, `mmaudio` hiçbir dosyaya girmiyor. Defter kendi kurulumunu yapıyor ve
tembel içe aktarım bu ayrımın kodda yaşayan hâli. Testler ellenmez. Ön yüz, `dist`, `package.json`
ellenmez. FOUNDATION.md'nin cümlesi de değişmiyor: hâlâ doğru, ve artık yanında makinenin
okuyabildiği bir karşılığı var.

## Nasıl görülecek

Dört komut da yeşil: **658**, **720**, 568, 584.

Ve asıl kanıt testte değil: sıfırdan bir cihaz artık
`pip install -r queen-agent/backend/requirements.txt` ile queen-agent'ı, aynısıyla queen-editor'ü
kurabiliyor — 31 Ağustos'ta olmayan şey buydu.
