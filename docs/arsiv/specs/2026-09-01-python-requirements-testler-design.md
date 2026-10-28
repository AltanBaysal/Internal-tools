# Python bağımlılıkları dosyada durur · Tur 1 (test) — Tasarım

**Kaynak:** 31 Ağustos'ta vite 8 test turunda çıkan hata, ve kullanıcının isteği *(1 Eylül)*.
**Numarasız:** vite 8 maddesinin gerekçesiyle aynı — Madde sayacı QueenAgent'ın ürün yol
haritasının, bu iş iki aracın kurulumuna dokunuyor.
**Dal:** `feat/python-requirements`.

## Sorun

`python -m pytest queen-editor -q` sıfırlanmış bir cihazda hiç başlamadı:

```
ModuleNotFoundError: No module named 'requests'
```

`backend/services/comfy/client.py` ve `backend/services/xai/client.py` modül düzeyinde
`import requests` yapıyor, ama
[queen-editor/backend/requirements.txt](../../../queen-editor/backend/requirements.txt) yalnız
`flask` ve `pytest` sayıyor. **Dosya, projenin ihtiyacını eksik söylüyor** — ve onu takip eden bir
kurulum çalışmayan bir depo bırakıyor.

queen-agent'ta durum bir adım daha kötü: **hiç `requirements.txt` yok.** `flask`'ın tek bağımlılık
olduğu [FOUNDATION.md](../../../queen-agent/FOUNDATION.md)'de bir cümle olarak yazıyor, ama `pip`
bir cümle okuyamaz.

Yıllardır oradaydı ve görünmedi, çünkü herkesin makinesinde `requests` başka bir sebeple zaten
kuruluydu. Cihazın sıfırlanması onu ilk kez ortaya çıkardı — yani bu, bulunması şansa kalmış bir
kusur, ve o yüzden çaresi bir test.

## Yol

İki iş, ve ikincisi birincinin tekrar olmamasını sağlıyor:

1. `queen-editor/backend/requirements.txt` `requests`'i sayar.
2. `queen-agent/backend/requirements.txt` doğar: `flask` ve `pytest`.

Ve ikisini de ayakta tutan bekçi: **kodun modül düzeyinde içe aktardığı her üçüncü parti paket,
o aracın `requirements.txt`'inde ilan edilmiş olmalı.**

## Bekçi nasıl bilecek

Statik bir liste değil — statik liste, koruduğu şeyle birlikte bayatlar. Test kodun kendisini
okuyor:

- Her `.py` dosyası `ast` ile ayrıştırılır ve **yalnız `tree.body`** taranır, yani modülün en üst
  düzeyi.
- Bulunan adlardan `sys.stdlib_module_names` *(Python 3.10'dan beri var)* ve yerel `backend`
  düşülür. Kalan, üçüncü parti kümesidir.
- Bu küme `requirements.txt`'in ilan ettiğinin **alt kümesi** olmalı.

### Neden yalnız modül düzeyi — ve bu maddenin kalbi bu

`torch`, `torchaudio` ve `mmaudio`
[mmaudio_sampler.py](../../../queen-editor/backend/features/photo_generation/data/mmaudio_sampler.py)'da
`render()`'ın **içinde** içe aktarılıyor. Bu bilinçli: GPU'ya bağlı, gigabaytlarca ağır, ve defter
onları ayrı kuruyor. `pytest queen-editor`'ün torch'suz bir cihazda 718 test koşabilmesinin sebebi
tam olarak o tembel içe aktarım.

Her içe aktarımı sayan bir test, torch'u `requirements.txt`'e sokmayı isterdi — ve o dosyayı takip
eden her geliştirici kurulumu CUDA ister hale gelirdi. Yani **ayrım süsleme değil**: modül düzeyi,
"içe aktarılmadan hiçbir şey çalışmaz" demek; fonksiyon içi, "bu yol seçilirse gerekir" demek.
Dosyanın işi birincisi.

Aynı sebeple `try/except ImportError` sarmalı ya da `if TYPE_CHECKING:` altındaki içe aktarımlar da
sayılmıyor: ikisi de `tree.body`'nin doğrudan çocuğu değil, ve ikisi de "olmayabilir" diyen
desenler.

## Bu turun testleri

Deseni `test_frontend_toolchain.py`'den *(31 Ağustos)*: repoyu inceleyen, aracının kendi test
klasöründe duran Python testi.

- `queen-agent/backend/tests/test_requirements.py` — **kırmızı**, dosya hiç yok
- `queen-editor/backend/tests/test_requirements.py` — **kırmızı**, `requests` eksik

Her biri iki şey söyler: dosya var, ve modül düzeyinde içe aktarılan her üçüncü parti paketi
sayıyor.

## Ayakta kalması gerekenler

Dört test komutunun tamamı: 656, 718, 568, 584. `test_frontend_toolchain.py`,
`test_dist_is_committed.py`.

## Bilerek yapılmayanlar

- **Sürüm tavanı yazmak.** Mevcut satırlar taban veriyor (`flask>=3.0`), ve yeni satırlar da öyle
  yazılır. Tavan, bugün var olmayan bir sorunu çözmek için yarının yamalarını kapatır.
- **`torch` ve arkadaşları.** Yukarıdaki gerekçe.
- **Bir kurulum betiği ya da `pyproject.toml`.** İki dosya iki satır çözüyor; ötesi istenmedi.
- **queen-editor'ün defterinin ne kurduğunu değiştirmek.** Defter kendi işini biliyor; bu madde
  geliştiricinin kurulumunu düzeltiyor.
