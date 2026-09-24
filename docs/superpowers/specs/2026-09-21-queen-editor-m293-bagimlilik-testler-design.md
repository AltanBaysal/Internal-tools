# Madde 293 — Bağımlılık tek kurala iniyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Maddenin kararı 21 Eylül'de verildi: *"cardlar ve üretimin asla
fotoğrafa bağlı olmaması lazım, bir sürü yapı var, esnek olması lazım sistemin."*

## Madde ne diyor

> **Bugün** iki kural var: ses videonun üstüne biner, ve her şey fotoğrafın üstüne. **Olacak:** tek
> kural kalıyor — **ses videoya bağlı**. Fotoğraf serbest: video artık fotoğraf beklemiyor, ve
> fotoğrafa kimse bağlı değil. Bir katman silinince giden şey *"üstündekiler"* değil, **ona bağlı
> olanlar** oluyor.

## Bugün kural nerede yazılı — üç yer

1. `domain/layers.py` · `can_produce`: `if slot == AUDIO: return is_taken(slots.get(VIDEO))`.
2. `domain/usecases/queue_layer.py` · `frames_in_scope`: `if kind == layers.AUDIO and (VIDEO not in
   held or VIDEO in broken)`.
3. `domain/usecases/remove_layer.py`: `over = queue.ORDER[queue.ORDER.index(kind):]` — *"katmanın
   kendisi ve üstündeki her şey."*

Üçü de bugün aynı cevabı veriyor, ama üçü ayrı cümle. Üçüncüsü ayrıca **yanlış** cevap veriyor:
`ORDER` bir *sıra*, bağımlılık değil. Fotoğraf sırada en altta olduğu için *"üstündekiler"* okuması
fotoğrafı silerken videoyu da götürüyor — oysa video fotoğrafa bağlı değil.

## Kural nereye yazılacak

`layers.py`, çünkü *"hangi katman neye bağlı"* katmanın kendi bilgisi, ve `domain/` dışarıdan hiçbir
şey import etmiyor *(CODE-STANDARD)*. Tek tablo:

- **`layers.NEEDS`** — bağımlılıklar. Bugün tek satır: ses videoya bağlı.
- **`layers.falls_with(kind)`** — o katman gidince kapanan yuvalar: katmanın kendisi, ve ona bağlı
  olanlar. Fotoğraf → yalnız fotoğraf. Video → video ve ses. Ses → yalnız ses.

Üç okuyucu da buradan okuyacak *(implementasyon turu)*. Bu tur yalnız **testi** yazar.

## Yazılacak testler

### `backend/tests/test_layers.py` — kuralın kendisi

1. **`test_the_dependency_rule_is_a_single_table`** — `layers.NEEDS` ses için videoyu veriyor;
   fotoğraf ve video tabloda yok. Bugün kırmızı: `NEEDS` yok.
2. **`test_a_layer_falls_with_what_depends_on_it`** — `falls_with(VIDEO)` video ile sesi veriyor,
   `falls_with(AUDIO)` yalnız sesi. Bugün kırmızı: `falls_with` yok.
3. **`test_nothing_depends_on_the_photo`** — `falls_with(PHOTO)` yalnız fotoğrafı veriyor. Maddenin
   kalbi, ve bugün kırmızı.

`can_produce`'un bugünkü testleri *(`test_audio_needs_a_video_under_it` ve komşuları)* aynen duruyor:
kural tabloya taşınırken davranış değişmiyor, ve onların yeşil kalması bunun kanıtı.

### `backend/tests/test_photo_usecases.py` — silme

4. **`test_deleting_the_photo_leaves_the_video_alone`** — fotoğrafı, videosu ve sesi olan bir karttan
   fotoğraf katmanı silinince yalnız fotoğrafın dosyası gidiyor; kayıtta video ve ses hâlâ duruyor.
   Bugün kırmızı: üçü birden siliniyor.
5. **`test_deleting_the_video_still_takes_the_sound_with_it`** — madde 31 yerinde duruyor. Bugün
   yeşil, ve öyle kalmalı: tabloya geçişin bir şeyi kırmadığını söyleyen bekçi.

### `backend/tests/test_photo_usecases.py` — üretim kapsamı

6. **`test_a_frame_with_no_photo_can_still_take_a_video`** — fotoğraf yuvası hiç dolmamış bir kart
   *(videodan doğan kart, madde 292)* video kapsamında. Maddenin *"görülür"* cümlesinin ilk yarısı.
7. **`test_sound_still_needs_a_video_under_it`** — videosu olmayan kart ses kapsamında değil,
   videosu olan kart kapsamda. Cümlenin ikinci yarısı, ve bugün yeşil.

## Bu turda yapılmayacaklar

- Fotoğrafın **ekrandan** silinebilir olması: `REMOVABLE` listesi ve arayüz *(madde 294)*.
- Fotoğrafsız kartın galeride nasıl çizildiği *(296)*, referans işinin doğurduğu kartlar *(303)*.
- Videonun render anında kaynak fotoğraf istemesi: o üreticinin kendi işi, ve referans kipi geldiğinde
  *(304)* kaynağı referanslar veriyor. Bu madde **kuralı** taşıyor, üreticiyi değil.

## Bitti sayılır

Dört test satırı koşulur; `python -m pytest queen-editor -q` kırmızı ve **kırmızılığın sebebi
beklenen sebep**: 1, 2, 3 tablo olmadığı için, 4 fotoğrafın videoyu da götürdüğü için. 5, 6 ve 7
bugün de yeşil — düşerlerse kural değil, testin kendisi yanlıştır. Kırmızı commit'lenir.
