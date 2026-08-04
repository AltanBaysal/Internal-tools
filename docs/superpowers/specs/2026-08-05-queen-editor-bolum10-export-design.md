# Queen Editor — Bölüm 10: Export

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 10
**Tasarım kaynağı:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html`
(<https://claude.ai/design/p/efad1f83-69d3-4e07-89fa-3783839c81c3>).

## Ne çalışır

App bar'daki **Export** düğmesi projeyi anlatan tek bir JSON dosyası indirir: en başta projenin
Drive'daki klasör yolu, ardından fotoğrafların dosya adı + prompt eşleşmesi, **galerideki güncel
sırayla**. Video hattı bu dosyayı okuyup kareleri aynı sırayla birleştirebilir — tasarımın kendi
notu: "Export → tek dosya: fotoğrafları prompt'larıyla eşleştiren liste, galeri sırasında +
projenin Drive'daki konumu (video bu sırayla birleştirilir)".

Düğme **her zaman aktiftir** — üretim sürerken ve hiç fotoğraf yokken de basılabilir; o an ne varsa
onu yazar.

## Kapsam dışı

- **Videonun kendisi** — yol haritasının sınırı burası: dosya üretilir, birleştirme başka aracın işi.
- **Export biçimi seçimi** (CSV, zip, fotoğrafların kendisi) — tek JSON, tasarımda başka biçim yok.
- **Negatif prompt ve seed alanları** — tasarım "fotoğrafları prompt'larıyla eşleştiren liste"
  diyor; iz zaten `photos.jsonl`'da duruyor, gerekirse ayrı bir iş olarak eklenir (YAGNI).
- **Yükleniyor/indiriliyor durumu** — tasarımda yok; dosya sunucuda anında üretiliyor
  (kayıt zaten okunmuş durumda), ara durum uydurulmaz.

## 1. Dosyanın içeriği

```json
{
  "folder": "/content/drive/MyDrive/<kök>/düğün",
  "photos": [
    { "file": "11_d.png", "prompt": "kraliçe tahtta, altın taç" },
    { "file": "11_c.png", "prompt": "kraliçe tahtta, altın taç" }
  ]
}
```

- `folder` — projenin Drive'daki mutlak klasör yolu (`PhotoStore.photo_dir`). Fotoğrafların tam yolu
  bu klasör + `file`'dır; her satırda yol tekrarlanmaz.
- `photos` — **galeri sırası** (Bölüm 9'un `order.json` + kayıt uzlaştırması). Sıra dosyanın
  anlamıdır: video bu sırayla birleşecek.
- Anahtarlar **İngilizce**: bu bir veri dosyası, ekran metni değil (repo dil kuralı — kullanıcıya
  görünen metin Türkçe, kod ve veri İngilizce). Dosyayı bir sonraki araç okuyacak.
- Fotoğraf yoksa `photos: []` — dosya yine iner. "Hiç yok" da bir cevaptır; boş dosya indirmek,
  düğmenin sessizce hiçbir şey yapmamasından dürüsttür.

## 2. Sunucu arayüzü

`GET /api/projects/<p>/export` → gövde yukarıdaki JSON, `Content-Disposition: attachment` ile
`<proje>-export.json` adıyla iner. Proje yoksa **404** (mevcut `ProjectMissing` deseni).

Neden ek (attachment) olarak sunucudan: dosyanın içeriğini sunucu zaten biliyor (klasör yolu yalnız
sunucunun bildiği bir şey — tarayıcı Drive'ı görmez), ve tarayıcı indirme işini kendi yapar; tarayıcıda
JSON kurup `Blob` indirmek aynı kuralın ikinci bir kopyasını doğurur (FOUNDATION §4: kural tek yerde).

**Dosya adı `<proje>-export.json`** — tasarım bir ad söylemiyor, bu bizim kararımız: indirilenler
klasöründe `düğün.json` tek başına ne olduğunu anlatmaz. Türkçe karakterler Flask'ın
`send_file(download_name=…)` işlevine bırakılır (RFC 5987 kodlamasını o üretir), elle başlık
kurulmaz.

## 3. Ekranda ne değişir

Tasarımdan birebir: app bar'ın sağ hücresi artık iki düğmelik bir gruptur —
`<div style={{ display: "flex", gap: 8, justifySelf: "end" }}>` içinde önce **Export**, sonra
**Projeden çık**; ikisi de `Btn ghost`, ikonsuz. Export'un yüklenme/pasif durumu yoktur.

**Deneme:** düğme görsel olarak tasarımdakiyle aynı kalır ama işaretlemede `<button>` değil,
indirme bağlantısı (`<a class="wf-btn wf-btn--ghost" href="…" download>`) olur. Gerekçe: yaptığı iş
bir dosya indirmek; bağlantı bunu tarayıcının kendi mekanizmasıyla yapar — JavaScript'e, `Blob`'a,
`window.location` oyununa gerek kalmaz, sağ tık → "bağlantıyı farklı kaydet" çalışır ve klavyeyle
erişilebilir kalır. `.wf-btn` zaten `display:inline-flex` ve kendi yazı tipini/rengini veriyor;
tek eksik, bağlantıların varsayılan alt çizgisi — o da `vendor/` değil `shared/app.css`'te
kapatılır (CODE-STANDARD: tasarım dosyası elle düzenlenmez). Bölüm 7'de proje kartının gerçek
`<button>`'a çevrilmesiyle aynı ilke: görünüm tasarımın, öğe işin doğrusu.

## 4. Doğrulama

1. 6 fotoğraflı projede sırala → Export → inen dosyada `photos` galerideki sırayla.
2. Dosyadaki `folder` Drive'daki gerçek klasör yolu; `folder` + `file` gerçek dosyayı gösteriyor.
3. Hiç fotoğrafı olmayan projede Export → `{"folder": …, "photos": []}` iner, hata yok.
4. Üretim sürerken Export → düğme aktif, o ana kadar üretilenleri içeren dosya iner.
5. Olmayan projenin export adresine gidilirse 404.

## Kararlar

- **Dosyayı sunucu üretir, tarayıcı yalnız indirir** — klasör yolunu ve sırayı zaten sunucu biliyor.
- **Anahtarlar İngilizce, dosya adı `<proje>-export.json`** — ikincisi tasarımda yok, bizim kararımız.
- **Export düğmesi bağlantı öğesi** (`<a>`), görünüm `Btn ghost` ile birebir aynı (§3).
- **Negatif/seed dışarıda** — tasarımın tarifi prompt eşleşmesi; iz kayıtta zaten var.
