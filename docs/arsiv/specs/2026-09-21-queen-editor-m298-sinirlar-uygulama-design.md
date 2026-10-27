# Madde 298 — Havuzun sınırları, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m298 test turu](2026-09-21-queen-editor-m298-sinirlar-testler-design.md),
`2503dd6e` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Dosyalar

**`data/ffmpeg_clips.py`** — `FfmpegClips.seconds(data)`: baytları geçici bir odaya yazar,
`ffprobe`'a süreyi sorar, odayı her hâlükârda siler. Hata `ffprobe`'un kendi son satırı; sayı
okunamazsa da hatadır, çünkü `ffprobe` anlamadığı bir dosya için 0 dönüp hiçbir şey söylemeyebiliyor.

**`data/reference_store.py`** — `names` yerine **`items`**: `[(ad, süre)]`. Süreyi yalnız klipler
için sorar *(fotoğrafın süresi yok)*, ve dosyanın **kendi yolundan** sorar: `ffprobe` başlıktan
okuduğu için dosya Drive'dan belleğe çekilmiyor. Klip aracını kurucudan alır — `MMAudioGenerator`'ın
`FfmpegAudio`'yu alması gibi, data içinde data.

**`domain/references.py`** — sınırlar ve `check(pool, incoming)`:

```
LIMITS = {picture: 9, video: 3, audio: 3}
CLIP   = (2, 15) saniye          # video ve ses
TOTAL  = 15 saniye               # videolar ayrı, sesler ayrı
```

Havuz ve gelenler aynı şekli taşıyor *(`{"name", "kind", "seconds"}`)*, çünkü kuralın ikisini
ayırması için bir sebep yok: sınır **ikisinin toplamına** bakıyor. Reddin cümlesi hangi sınır ve
hangi dosya olduğunu söyler.

**`domain/usecases/list_references.py`** — satır artık `seconds` taşıyor.

**`domain/usecases/add_references.py`** — `clips` alır; gelen kliplerin süresini sorar, kuralı bir
kez çağırır, **sonra** yazar. Süresi okunamayan klip `PoolLimit`'e çevrilir — kapının tek bir şeyi
çevirmesi için, ve kullanıcı için ikisi de aynı cevaptır: bu dosya havuza giremez, sebebi şu.

**`presentation/reference_routes.py`** ve **`main.py`** — yeni araç kurulur ve bağlanır.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
